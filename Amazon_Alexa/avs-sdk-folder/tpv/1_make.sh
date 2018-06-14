    mkdir /home/pi/SmartSpeakerDemo/Amazon_Alexa/avs-sdk-folder/build

    sudo chmod 755 -R /home/pi/SmartSpeakerDemo/Amazon_Alexa/avs-sdk-folder/third-party/portaudio
    cd /home/pi/SmartSpeakerDemo/Amazon_Alexa/avs-sdk-folder/third-party/portaudio
    ./configure --without-jack
    make

    cd /home/pi/SmartSpeakerDemo/Amazon_Alexa/avs-sdk-folder/build
    cmake /home/pi/SmartSpeakerDemo/Amazon_Alexa/avs-sdk-folder/avs-device-sdk \
    -DSENSORY_KEY_WORD_DETECTOR=ON \
    -DSENSORY_KEY_WORD_DETECTOR_LIB_PATH=/home/pi/SmartSpeakerDemo/Amazon_Alexa/avs-sdk-folder/third-party/alexa-rpi/lib/libsnsr.a \
    -DSENSORY_KEY_WORD_DETECTOR_INCLUDE_DIR=/home/pi/SmartSpeakerDemo/Amazon_Alexa/avs-sdk-folder/third-party/alexa-rpi/include \
    -DGSTREAMER_MEDIA_PLAYER=ON -DPORTAUDIO=ON \
    -DPORTAUDIO_LIB_PATH=/home/pi/SmartSpeakerDemo/Amazon_Alexa/avs-sdk-folder/third-party/portaudio/lib/.libs/libportaudio.a \
    -DPORTAUDIO_INCLUDE_DIR=/home/pi/SmartSpeakerDemo/Amazon_Alexa/avs-sdk-folder/third-party/portaudio/include \
    -DACSDK_EMIT_SENSITIVE_LOGS=ON \
    -DCMAKE_BUILD_TYPE=DEBUG

    cd /home/pi/SmartSpeakerDemo/Amazon_Alexa/avs-sdk-folder/build
    make SampleApp -j2

    cp /home/pi/SmartSpeakerDemo/Amazon_Alexa/avs-sdk-folder/build/SampleApp/src/SampleApp /home/pi/SmartSpeakerDemo/Amazon_Alexa/SampleApp_For_Pi3

    cp /home/pi/SmartSpeakerDemo/Amazon_Alexa/avs-sdk-folder/tpv/AlexaClientSDKConfig.json /home/pi/SmartSpeakerDemo/Amazon_Alexa/avs-sdk-folder/build/Integration/
