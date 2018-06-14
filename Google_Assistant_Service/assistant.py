# Copyright (C) 2017 Google Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""Sample that implements a gRPC client for the Google Assistant API."""

import concurrent.futures
import json
import logging
import os
import os.path
import pathlib2 as pathlib
import sys
import uuid

import click
import grpc
import google.auth.transport.grpc
import google.auth.transport.requests
import google.oauth2.credentials

from snowboy import snowboydecoder
import sys
import signal
import time
import logging

import globalmodule

from google.assistant.embedded.v1alpha2 import (
    embedded_assistant_pb2,
    embedded_assistant_pb2_grpc
)
from tenacity import retry, stop_after_attempt, retry_if_exception

try:
    from helpers import (
        assistant_helpers,
        audio_helpers,
        device_helpers
    )
except (SystemError, ImportError):
    import assistant_helpers
    import audio_helpers
    import device_helpers


ASSISTANT_API_ENDPOINT = 'embeddedassistant.googleapis.com'
END_OF_UTTERANCE = embedded_assistant_pb2.AssistResponse.END_OF_UTTERANCE
DIALOG_FOLLOW_ON = embedded_assistant_pb2.DialogStateOut.DIALOG_FOLLOW_ON
CLOSE_MICROPHONE = embedded_assistant_pb2.DialogStateOut.CLOSE_MICROPHONE
DEFAULT_GRPC_DEADLINE = 60 * 3 + 5


class Assistant(object):
    """Sample Assistant that supports conversations and device actions.

    Args:
      device_model_id: identifier of the device model.
      device_id: identifier of the registered device instance.
      conversation_stream(ConversationStream): audio stream
        for recording query and playing back assistant answer.
      channel: authorized gRPC channel for connection to the
        Google Assistant API.
      deadline_sec: gRPC deadline in seconds for Google Assistant API call.
      device_handler: callback for device actions.
    """

    """def __init__(self, language_code, device_model_id, device_id,
                 conversation_stream,
                 channel, deadline_sec, device_handler):"""

    def update_state(self,state):
        try:
            state_file = open('dialog_state', 'w')
            state_file.write(state)
        finally:
            if state_file:
                state_file.close()

    def update_data(self,data):
        try:
            data_file = open('card_data', 'w')
            data_file.write(data)
        finally:
            if data_file:
                data_file.close()

    def __init__(self):
        
        self.api_endpoint = ASSISTANT_API_ENDPOINT
        self.credentials = os.path.join(click.get_app_dir('google-oauthlib-tool'),
                                   'credentials.json')
        self.project_id = 'tpvsmartdemo'
        self.device_model_id = 'tpvsmartdemo-googlepi-7rwwpw'
        self.device_config = os.path.join(click.get_app_dir('googlesamples-assistant'),
                                   'device_config.json')
        self.language_code = 'en-US'
        self.audio_sample_rate = audio_helpers.DEFAULT_AUDIO_SAMPLE_RATE
        self.audio_sample_width = audio_helpers.DEFAULT_AUDIO_SAMPLE_WIDTH
        self.audio_iter_size = audio_helpers.DEFAULT_AUDIO_ITER_SIZE
        self.audio_block_size = audio_helpers.DEFAULT_AUDIO_DEVICE_BLOCK_SIZE
        self.audio_flush_size = audio_helpers.DEFAULT_AUDIO_DEVICE_FLUSH_SIZE
        self.grpc_deadline = DEFAULT_GRPC_DEADLINE
        #self.device_handler = device_handler
        #self.device_id = device_id
        #self.conversation_stream = conversation_stream
        
        # Setup self.logging.
        logging.basicConfig() #if verbose else self.logging.INFO)
        self.logging = logging.getLogger('ASSISTANT')
        self.logging.setLevel(logging.DEBUG)  

        # Opaque blob provided in AssistResponse that,
        # when provided in a follow-up AssistRequest,
        # gives the Assistant a context marker within the current state
        # of the multi-Assist()-RPC "conversation".
        # This value, along with MicrophoneMode, supports a more natural
        # "conversation" with the Assistant.
        self.conversation_state = None

        self.current_state = "Online"

        # Load OAuth 2.0 credentials.
        try:
            with open(self.credentials, 'r') as f:
                self.credentials = google.oauth2.credentials.Credentials(token=None,
                                                                **json.load(f))
                self.http_request = google.auth.transport.requests.Request()
                self.credentials.refresh(self.http_request)
        except Exception as e:
            self.logging.error('Error loading credentials: %s', e)
            self.logging.error('Run google-oauthlib-tool to initialize '
                          'new OAuth 2.0 credentials.')
            return

        # Create an authorized gRPC channel.
        self.grpc_channel = google.auth.transport.grpc.secure_authorized_channel(
            self.credentials, self.http_request, self.api_endpoint)
        self.logging.info('Connecting to %s', self.api_endpoint)

        # Create Google Assistant API gRPC client.
        self.assistant = embedded_assistant_pb2_grpc.EmbeddedAssistantStub(
            self.grpc_channel
        )

        try:
            with open(self.device_config) as f:
                self.device = json.load(f)
                self.device_id = self.device['id']
                self.device_model_id = self.device['model_id']
                self.logging.info("Using device model %s and device id %s",
                                self.device_model_id,
                                self.device_id)
        except Exception as e:
            self.logging.warning('Device config not found: %s' % e)
            self.logging.info('Registering device')
            if not self.device_model_id:
                self.logging.error('Option --device-model-id required '
                                   'when registering a device instance.')

            if not self.project_id:
                self.logging.error('Option --project-id required '
                                   'when registering a device instance.')

            device_base_url = (
                'https://%s/v1alpha2/projects/%s/devices' % (self.api_endpoint,
                                                             self.project_id)
            )
            self.device_id = str(uuid.uuid1())
            payload = {
                'id': self.device_id,
                'model_id': self.device_model_id,
                'client_type': 'SDK_SERVICE'
            }
            self.session = google.auth.transport.requests.AuthorizedSession(
                self.credentials
            )
            r = self.session.post(device_base_url, data=json.dumps(payload))
            if r.status_code != 200:
                self.logging.error('Failed to register device: %s', r.text)
   
            self.logging.info('Device registered: %s', self.device_id)
            pathlib.Path(os.path.dirname(self.device_config)).mkdir(exist_ok=True)
            with open(self.device_config, 'w') as f:
                json.dump(payload, f)

        device_handler = device_helpers.DeviceRequestHandler(self.device_id)
        self.logging.info('Init Google Assistant Success')
        self.current_state = "Online"
        self.user_request = ""
        self.update_state("Online")
        self.update_data("")

    """def __enter__(self):
        print("__enter__(self)")
        return self

    def __exit__(self, etype, e, traceback):
        print("__exit__(self, etype, e, traceback)")
        if e:
            return False
        self.conversation_stream.close()"""

    def assist(self):
        """Send a voice request to the Assistant and playback the response.

        Returns: True if conversation should continue.
        """
        self.audio_device = None
        self.audio_source = self.audio_device = (
            self.audio_device or audio_helpers.SoundDeviceStream(
                sample_rate=self.audio_sample_rate,
                sample_width=self.audio_sample_width,
                block_size=self.audio_block_size,
                flush_size=self.audio_flush_size
            )
        )

        self.audio_sink = self.audio_device = (
            self.audio_device or audio_helpers.SoundDeviceStream(
                sample_rate=self.audio_sample_rate,
                sample_width=self.audio_sample_width,
                block_size=self.audio_block_size,
                flush_size=self.audio_flush_size
            )
        )
        
        # Create conversation stream with the given audio source and sink.
        self.conversation_stream = audio_helpers.ConversationStream(
            source=self.audio_source,
            sink=self.audio_sink,
            iter_size=self.audio_iter_size,
            sample_width=self.audio_sample_width,
        )
        restart = False
        continue_dialog = True
        user_speak_request = False
        try:
            while continue_dialog:
                continue_dialog = False
                self.conversation_stream.start_recording()
                self.logging.info('Recording audio request!!!')
                self.logging.info('Please speak a new request to Google Assistant!!!')

                def iter_assist_requests():
                    for c in self.gen_assist_requests():
                        assistant_helpers.log_assist_request_without_audio(c)
                        yield c
                    self.conversation_stream.start_playback()
                    globalmodule.snowboycontroller = True

                # This generator yields AssistResponse proto messages
                # received from the gRPC Google Assistant API.
                for resp in self.assistant.Assist(iter_assist_requests(),
                                                  self.grpc_deadline):
                    assistant_helpers.log_assist_response_without_audio(resp)
                    if resp.event_type == END_OF_UTTERANCE:
                        current_time= time.strftime("%Y-%m-%d %H:%M:%S",time.localtime(time.time()))
                        self.logging.info('End of audio request detected'+current_time)
                        self.conversation_stream.stop_recording()
                        self.current_state = "Recognizing"
                    if resp.speech_results:
                        self.logging.info('Transcript of user request: "%s".',
                                     ' '.join(r.transcript
                                              for r in resp.speech_results))
                        self.logging.info('Playing assistant response.')
                        if "Recognizing" in self.current_state:
                            self.user_request = ' '.join(r.transcript for r in resp.speech_results)
                            self.update_state("Thinking")
                            self.current_state = "Thinking"
                    if len(resp.audio_out.audio_data) > 0:
                        #self.logging.info('resp.audio_out.audio_data')
                        user_speak_request = True
                        if globalmodule.hotworddetected:  
                            break
                        else:
                            self.conversation_stream.write(resp.audio_out.audio_data)
                    if resp.dialog_state_out.conversation_state:
                        conversation_state = resp.dialog_state_out.conversation_state
                        self.logging.debug('Updating conversation state.')
                        self.conversation_state = conversation_state
                    if resp.dialog_state_out.volume_percentage != 0:
                        volume_percentage = resp.dialog_state_out.volume_percentage
                        self.conversation_stream.volume_percentage = volume_percentage
                    if resp.dialog_state_out.microphone_mode == DIALOG_FOLLOW_ON:
                        continue_conversation = True
                        self.logging.info('Expecting follow-on query from user.')
                    if resp.dialog_state_out.supplemental_display_text:
                        current_time= time.strftime("%Y-%m-%d %H:%M:%S",time.localtime(time.time()))
                        self.logging.info('Response Text: "%s"'+current_time, resp.dialog_state_out.supplemental_display_text)
                        if "Thinking" in self.current_state:
                            data = {'ask': self.user_request,'answer': resp.dialog_state_out.supplemental_display_text}
                            self.update_data(json.dumps(data))
                            self.update_state("Speaking")

                self.logging.info('Finished playing assistant response.')

                self.current_state = "Online"
                self.update_state("Online")
                self.update_data("")

                self.conversation_stream.stop_playback()
                
                if not user_speak_request:
                    #User says a hotword but he doesn't have a request
                    globalmodule.snowboycontroller = True
                    self.conversation_stream.stop_recording()
                    self.conversation_stream.closeSource()
                else:
                    user_speak_request=False
        except Exception as e:
            self._create_assistant()
            self.logging.exception('Skipping because of connection reset')
            restart = True
        try:
            self.logging.info('conversation_stream.closeSink()')
            self.conversation_stream.closeSink()
            if restart:
                self.logging.info('Exception and Restart assistant')
                self.assist()
        except Exception:
            self.logging.error('Failed to close conversation_stream.')

    def _create_assistant(self):
        # Create gRPC channel
        grpc_channel = google.auth.transport.grpc.secure_authorized_channel(
            self.credentials, self.http_request, self.api_endpoint)
        self.logging.info('Connecting to %s', self.api_endpoint)
        
        # Create Google Assistant API gRPC client.
        self.assistant = embedded_assistant_pb2_grpc.EmbeddedAssistantStub(self.grpc_channel)

    def is_grpc_error_unavailable(e):
        is_grpc_error = isinstance(e, grpc.RpcError)
        if is_grpc_error and (e.code() == grpc.StatusCode.UNAVAILABLE):
            self.logging.error('grpc unavailable error: %s', e)
            return True
        return False

    @retry(reraise=True, stop=stop_after_attempt(3),
           retry=retry_if_exception(is_grpc_error_unavailable))

    def gen_assist_requests(self):
        """Yields: AssistRequest messages to send to the API."""

        dialog_state_in = embedded_assistant_pb2.DialogStateIn(
                language_code=self.language_code,
                conversation_state=b''
            )
        if self.conversation_state:
            self.logging.debug('Sending conversation state.')
            dialog_state_in.conversation_state = self.conversation_state
        config = embedded_assistant_pb2.AssistConfig(
            audio_in_config=embedded_assistant_pb2.AudioInConfig(
                encoding='LINEAR16',
                sample_rate_hertz=self.conversation_stream.sample_rate,
            ),
            audio_out_config=embedded_assistant_pb2.AudioOutConfig(
                encoding='LINEAR16',
                sample_rate_hertz=self.conversation_stream.sample_rate,
                volume_percentage=self.conversation_stream.volume_percentage,
            ),
            dialog_state_in=dialog_state_in,
            device_config=embedded_assistant_pb2.DeviceConfig(
                device_id=self.device_id,
                device_model_id=self.device_model_id,
            )
        )
        # The first AssistRequest must contain the AssistConfig
        # and no audio data.
        yield embedded_assistant_pb2.AssistRequest(config=config)
        for data in self.conversation_stream:
            # Subsequent requests need audio data, but not config.
            yield embedded_assistant_pb2.AssistRequest(audio_in=data)


"""@click.command()
@click.option('--api-endpoint', default=ASSISTANT_API_ENDPOINT,
              metavar='<api endpoint>', show_default=True,
              help='Address of Google Assistant API service.')
@click.option('--credentials',
              metavar='<credentials>', show_default=True,
              default=os.path.join(click.get_app_dir('google-oauthlib-tool'),
                                   'credentials.json'),
              help='Path to read OAuth2 credentials.')
@click.option('--project-id',
              metavar='<project id>',
              help=('Google Developer Project ID used for registration '
                    'if --device-id is not specified'))
@click.option('--device-model-id',
              metavar='<device model id>',
              help=(('Unique device model identifier, '
                     'if not specifed, it is read from --device-config')))
@click.option('--device-id',
              metavar='<device id>',
              help=(('Unique registered device instance identifier, '
                     'if not specified, it is read from --device-config, '
                     'if no device_config found: a new device is registered '
                     'using a unique id and a new device config is saved')))
@click.option('--device-config', show_default=True,
              metavar='<device config>',
              default=os.path.join(
                  click.get_app_dir('googlesamples-assistant'),
                  'device_config.json'),
              help='Path to save and restore the device configuration')
@click.option('--lang', show_default=True,
              metavar='<language code>',
              default='en-US',
              help='Language code of the Assistant')
@click.option('--verbose', '-v', is_flag=True, default=False,
              help='Verbose self.logging.')
@click.option('--input-audio-file', '-i',
              metavar='<input file>',
              help='Path to input audio file. '
              'If missing, uses audio capture')
@click.option('--output-audio-file', '-o',
              metavar='<output file>',
              help='Path to output audio file. '
              'If missing, uses audio playback')
@click.option('--audio-sample-rate',
              default=audio_helpers.DEFAULT_AUDIO_SAMPLE_RATE,
              metavar='<audio sample rate>', show_default=True,
              help='Audio sample rate in hertz.')
@click.option('--audio-sample-width',
              default=audio_helpers.DEFAULT_AUDIO_SAMPLE_WIDTH,
              metavar='<audio sample width>', show_default=True,
              help='Audio sample width in bytes.')
@click.option('--audio-iter-size',
              default=audio_helpers.DEFAULT_AUDIO_ITER_SIZE,
              metavar='<audio iter size>', show_default=True,
              help='Size of each read during audio stream iteration in bytes.')
@click.option('--audio-block-size',
              default=audio_helpers.DEFAULT_AUDIO_DEVICE_BLOCK_SIZE,
              metavar='<audio block size>', show_default=True,
              help=('Block size in bytes for each audio device '
                    'read and write operation.'))
@click.option('--audio-flush-size',
              default=audio_helpers.DEFAULT_AUDIO_DEVICE_FLUSH_SIZE,
              metavar='<audio flush size>', show_default=True,
              help=('Size of silence data in bytes written '
                    'during flush operation'))
@click.option('--grpc-deadline', default=DEFAULT_GRPC_DEADLINE,
              metavar='<grpc deadline>', show_default=True,
              help='gRPC deadline in seconds')
@click.option('--once', default=False, is_flag=True,
              help='Force termination after a single conversation.')"""
"""def main(api_endpoint, credentials, project_id,
         device_model_id, device_id, device_config, lang, verbose,
         input_audio_file, output_audio_file,
         audio_sample_rate, audio_sample_width,
         audio_iter_size, audio_block_size, audio_flush_size,
         grpc_deadline, once, *args, **kwargs):"""

"""Samples for the Google Assistant API.

    Examples:
      Run the sample with microphone input and speaker output:

        $ python -m googlesamples.assistant

      Run the sample with file input and speaker output:

        $ python -m googlesamples.assistant -i <input file>

      Run the sample with file input and output:

        $ python -m googlesamples.assistant -i <input file> -o <output file>
    """

"""
    @device_handler.command('action.devices.commands.OnOff')
    def onoff(on):
        if on:
            self.logging.info('Turning device on')
        else:
            self.logging.info('Turning device off')

    with Assistant(lang, device_model_id, device_id,
                         conversation_stream,
                         grpc_channel, grpc_deadline,
                         device_handler) as assistant:
        # If file arguments are supplied:
        # exit after the first turn of the conversation.
        if input_audio_file or output_audio_file:
            assistant.assist()
            return

        # If no file arguments supplied:
        # keep recording voice requests using the microphone
        # and playing back assistant response using the speaker.
        # When the once flag is set, don't wait for a trigger. Otherwise, wait.
        wait_for_user_trigger = not once
        while True:
            if wait_for_user_trigger:
                click.pause(info='Press Enter to send a new request...')
            continue_conversation = assistant.assist()
            # wait for user trigger if there is no follow-up turn in
            # the conversation.
            wait_for_user_trigger = not continue_conversation

            # If we only want one conversation, break.
            if once and (not continue_conversation):
                break


if __name__ == '__main__':
    main()
"""
