from picamera2 import Picamera2, Preview
from libcamera import Transform
from time import sleep

picam2 = Picamera2()
camera_config = picam2.create_preview_configuration(transform=Transform(vflip=True))
picam2.configure(camera_config)
picam2.start_preview(Preview.QTGL)
picam2.start()

dirName = '4August2022Photos'
for i in range(0,1000):
    picam2.capture_file("{dirName}/skyNum%s.jpg" % i)
    sleep(20)

# Basic script that collects photos. Can use them to train/test classification algorithm.
# May need to change/create directory to save them to, delay between photo, change naming convention etc.