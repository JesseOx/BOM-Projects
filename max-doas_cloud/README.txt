eg_pics contains a few folders of original photos that can be used to test classification algorithm
This folder also contains a few folders of photos that have been run through imageClasswrite.py with different parameters.

literature contains a file from Stephen regarding potential tasks for the cloud classifcation. It also contains all referenced
literature articles on the max-doas and cloud classification problem.

scripts contains all scripts associated with this project.

imageClassify is a script that can either run through an entire directory of photos or a single photo.
It then outputs the classified version of the photo/s. It can be used for refining the classification parameters.
Make sure all folders/image that are being INPUT and OUTPUT exist. 

imageCollector is a script that simply collects photos from the Pi module using the picam2 library.
This is useful for collecting photos to refine the classification script.
This could also be used to build a library for ML training. A possible ML algorithm could be kNN clustering.
Create amt of clusters for each class of sky (clear, cloudy, partly cloudy) Further work required for this

imageCCS (image capture, classify, store) is the main script that would be running on the deployed Pi.
It does as the name suggests and captures a photo when a signal is set. It then stores the raw photo in a directory
of the days date and saves the file as the exact time it was taken. It will then store a classified version of the photo.
The program will also True if it considers clear and False if not.

The classification currently solely uses RGB values of the image to return a True or False value. This is a fairly effective method 
but it is somewhat rudimentary and has a few weaknesses. The algorithm will not work at night time and it's performance will
suffer toward dawn/dusk. As written above machine learning algorithms are a possibility for cloud classifcation. Cloud object 
detection would also be another option.

DO NOT upgrade/update any software/libraries as the release of picamera2 that the script uses is very clunky and half finished.
It is expected they will change the library extensively in the future and it will break the scripts.



