from PIL import Image, ImageDraw, ImageFont
import extcolors
import os

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

def dirClassify(folder):
    centreCoords = (280, 200, 360, 280)
    imageNum = 0
    font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSerif.ttf", 50)

    for image in os.listdir(folder):
        imageNum += 1
        print('Classifying image {}'.format(imageNum))
        skyPicOpen = Image.open(r'{}/{}'.format(folder, image))
        cropped_photo = skyPicOpen.crop(centreCoords)
        x = is_clear(cropped_photo)
        text = '% blue : {:.2f} \n is clear: {}'.format(blueStrength, x)
        skyPicDraw = ImageDraw.Draw(skyPicOpen)
        skyPicDraw.text((20,20), text, fill=(255,0,0), font=font)
        skyPicDraw.rectangle(centreCoords, outline='black')
        skyPicOpen.save(r'classPhotos/classified{}.png'.format(image))

def oneClassify(path):
    skyPicOpen = Image.open(path)
    centreCoords = (280, 200, 360, 280)
    cropped_photo = skyPicOpen.crop(centreCoords)
    is_clear(cropped_photo)

    font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSerif.ttf", 50)
    text = '% blue : {:.2f} \n is clear: {}'.format(blueStrength, is_clear(cropped_photo))
    skyPicDraw = ImageDraw.Draw(skyPicOpen)
    skyPicDraw.text((20,20), text, fill=(255,0,0), font=font)
    skyPicDraw.rectangle(centreCoords, outline='black')
    skyPicOpen.save('draw.png')

#oneClassify(r"12July2022Photos/skyNum11.jpg")

dirClassify('trickypics')
