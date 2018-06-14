export LD_LIBRARY_PATH=/home/pi/SmartSpeakerDemo/Iflytek/libs/arm
cd Iflytek/bin
sudo chmod 755 voice_control
./voice_control & cd ../..
sudo python3 demo_main.py --sdk_type Iflytek