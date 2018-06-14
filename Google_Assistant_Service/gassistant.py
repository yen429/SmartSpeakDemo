from snowboy import snowboydecoder
import sys
import signal
import time
import logging
from assistant import Assistant
import globalmodule
import threading

interrupted=False

logging.basicConfig()
logger = logging.getLogger("DAEMON")
logger.setLevel(logging.DEBUG)

if len(sys.argv) == 1:
    logger.info("Error: need to specify model name")
    logger.info("Usage: python demo.py your.model")
    sys.exit(-1)

def signal_handler(signal, frame):
    global interrupted
    interrupted = True


def interrupt_callback():
    global interrupted
    return interrupted

model = sys.argv[1]

# capture SIGINT signal, e.g., Ctrl+C
signal.signal(signal.SIGINT, signal_handler)

detector = snowboydecoder.HotwordDetector(model, sensitivity=0.7)
assistant = Assistant()

def snowboy_detect_controller():
    def detect_callback():
        detector.terminate()
        snowboydecoder.play_audio_file(snowboydecoder.DETECT_DING)
        globalmodule.assistantcontroller=True
        globalmodule.hotworddetected=False
        while True:
            if globalmodule.snowboycontroller:
                globalmodule.snowboycontroller=False
                logger.info('Listening... Press Ctrl+C to exit')
                detector.start(detected_callback=detect_callback, interrupt_check=interrupt_callback, sleep_time=0.03)
    
    # main loop
    globalmodule.snowboycontroller=False
    logger.info('Listening... Press Ctrl+C to exit')
    detector.start(detected_callback=detect_callback, interrupt_check=interrupt_callback, sleep_time=0.03)


def assistant_detect_controller():
    while True:
        if globalmodule.assistantcontroller:
            globalmodule.assistantcontroller=False
            assistant.assist()
            snowboydecoder.play_audio_file(snowboydecoder.DETECT_DONG)

threading.Thread(target=snowboy_detect_controller).start()
threading.Thread(target=assistant_detect_controller).start()

#logger.info('detector.terminate()')
#detector.terminate()

