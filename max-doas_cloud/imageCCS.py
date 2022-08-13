from picamera2 import Picamera2, Preview
from PIL import Image, ImageDraw, ImageFont
from datetime import datetime
import os
import extcolors
import time

def rgb_inten(r,g,b):
    x = 1/3*(r/255 + g/255 + b/255)
    return x

def is_clear(picture):
    # Tolerance is the colour grouping strength. 0 won't group anything and 100 will group everything
    # Limit is the upper limit of extracted colours
    colours_x = extcolors.extract_from_image(picture, tolerance=1, limit=20)
    #print(colours_x)
    global blueStrength
    blueStrength, totalOccur = 0, 0
    minSum, maxSum = 766, 0 # Greater than the highest possible RGB val, smaller than smallest possible RGB val

    # colours_x returns a tuple of tuples
    # First item in the tuple is the RBG value (this goes from most-least common in the tuple)
    # Second item in the tuple is how many pixels contain this value
    for items in colours_x[0]:
        rgbVal = items[0]
        redVal, greenVal, blueVal = rgbVal[0], rgbVal[1], rgbVal[2]
        # if the current min is bigger, then set these values to the min
        if minSum > redVal + greenVal + blueVal:
            minSum = redVal + greenVal + blueVal
        # if the current max is smaller, then set these values to the max
        if maxSum < redVal + greenVal + blueVal:
            maxSum = redVal + greenVal + blueVal
        # if redVal < 100 and 90 <= greenVal <= 200 and blueVal >= 150 and rgb_inten(redVal,greenVal,blueVal) <= 0.8:
        if 40 <= redVal <= 120 and 60 <= greenVal <= 200 and blueVal >= 135 and rgb_inten(redVal,greenVal,blueVal) <= 0.8:
            blueStrength += items[1]
        totalOccur += items[1]
    sumDelta = maxSum - minSum
    blueStrength = blueStrength / totalOccur
    # print('Overall blue percentage: %.2f' % blueStrength)
    # Set blueness threshold to >= 80%
    if blueStrength >= 0.8 and sumDelta <= 50:
        return True
    else:
      	return False

def dir_mgmt():
    global today, fullToday
    today = datetime.now().strftime('%d-%b-%Y')
    fullToday = datetime.now().strftime('%y%m%d_%H%M%S')
    path = r'/home/pi/Documents/max-doas/{}'.format(today)
    dirExists = os.path.exists(path)

    if not dirExists:
        os.mkdir(path)

scanSignal = True
# instrum = solys() Pseudo code for when/if we get instrument inputs

picam2 = Picamera2()
picam2.start()

def run_script():
    dir_mgmt()

    if scanSignal:
        # Later add instrum.angle that would also include altitude angle in file name
        picam2.capture_file('/home/pi/Documents/max-doas/{}/{}.jpg'.format(today, fullToday))
        skyPicOpen = Image.open('/home/pi/Documents/max-doas/{}/{}.jpg'.format(today, fullToday))

        centreCoords = (280, 200, 360, 280)
        cropped_photo = skyPicOpen.crop(centreCoords)
        x = is_clear(cropped_photo)
            
        font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSerif.ttf", 50)
        text = '% blue : {:.2f} \n is clear: {}'.format(blueStrength, is_clear(cropped_photo))
        skyPicDraw = ImageDraw.Draw(skyPicOpen)
        skyPicDraw.text((20,20), text, fill=(255,0,0), font=font)
        skyPicDraw.rectangle(centreCoords, outline='black')
        skyPicOpen.save('/home/pi/Documents/max-doas/{}/{}C.jpg'.format(today, fullToday))
        return x
    
while True:
    run_script()
    time.sleep(20)
    
    
# Script: Image CAPTURE, CLASSIFY, STORE
# Currently since we don't have instrument inputs from the SOLYS we use static variable scanSignal to trigger the photo and classification
# It then just sleeps and takes another photo
# When instrument input is working you would not need to sleep and just get the if statement to run the photo/classification stuff when the SOLYS changes its altitude angle


