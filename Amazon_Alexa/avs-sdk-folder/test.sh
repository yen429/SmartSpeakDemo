echo
echo "==============> BUILDING Tests =============="
echo
mkdir -p "/home/pi/avs-sdk-folder/avs-device-sdk/KWD/inputs/SensoryModels/"
cp "/home/pi/avs-sdk-folder/third-party/alexa-rpi/models/spot-alexa-rpi-31000.snsr" "/home/pi/avs-sdk-folder/avs-device-sdk/KWD/inputs/SensoryModels/"
cd /home/pi/avs-sdk-folder/build
make all test -j2
chmod +x "/home/pi/avs-sdk-folder/startsample.sh"
chmod +x "/home/pi/avs-sdk-folder/startauth.sh"
