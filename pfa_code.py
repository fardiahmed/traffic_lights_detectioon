#!/usr/bin/python
import cv2 as cv
import numpy as np
import RPi.GPIO as GPIO
from scipy.stats import itemfreq
import time
#set GPIO numbering mode and define output pins
GPIO.setmode(GPIO.BOARD)
GPIO.setwarnings(False)
GPIO.setup(31,GPIO.OUT)
GPIO.setup(33,GPIO.OUT)
GPIO.setup(35,GPIO.OUT)
GPIO.setup(37,GPIO.OUT)
GPIO.setup(12, GPIO.OUT)
GPIO.setup(32, GPIO.OUT)
p1 = GPIO.PWM(12, 100)
p2 = GPIO.PWM(32, 100)
p1.start(0)
p2.start(0)
p1.ChangeDutyCycle(2)
p2.ChangeDutyCycle(2)#droite
def forward():
    GPIO.output(31,True)
    GPIO.output(33,False)
    GPIO.output(35,False)
    GPIO.output(37,True)
def turn_right():
    GPIO.output(31,False)
    GPIO.output(33,True)
    GPIO.output(35,False)
    GPIO.output(37,True)
def turn_left():
    GPIO.output(31,True)
    GPIO.output(33,False)
    GPIO.output(35,True)
    GPIO.output(37,False)
def stop():
    GPIO.output(31,False)
    GPIO.output(33,False)
    GPIO.output(35,False)
    GPIO.output(37,False)
def back():
    GPIO.output(31,False)
    GPIO.output(33,True)
    GPIO.output(35,True)
    GPIO.output(37,False)
# I took this solution from:
# https://stackoverflow.com/questions/43111029/how-to-find-the-average-colour-of-an-image-in-python-with-opencv#43111221
def get_dominant_color(image, n_colors):
    pixels = np.float32(image).reshape((-1, 3))
    criteria = (cv.TERM_CRITERIA_EPS + cv.TERM_CRITERIA_MAX_ITER, 200, .1)
    flags = cv.KMEANS_RANDOM_CENTERS
    flags, labels, centroids = cv.kmeans(
        pixels, n_colors, None, criteria, 10, flags)
    palette = np.uint8(centroids)
    return palette[np.argmax(itemfreq(labels)[:, -1])]


clicked = False
def onMouse(event, x, y, flags, param):
    global clicked
    if event == cv.EVENT_LBUTTONUP:
        clicked = True


cameraCapture = cv.VideoCapture(0)  # Put here ID of your camera (/dev/videoN)
cv.namedWindow('camera')
cv.setMouseCallback('camera', onMouse)

# Read and process frames in loop
success, frame = cameraCapture.read()
while success and not clicked:
    p1.ChangeDutyCycle(40)
    p2.ChangeDutyCycle(40)
    cv.waitKey(1)
    success, frame = cameraCapture.read()

    # Conversion to gray is required to speed up calculations, we would detect
    # the same circles in BGR and GRAY anyways.
    gray = cv.cvtColor(frame, cv.COLOR_BGR2GRAY)
    # Then we blur the entire frame to prevent accidental false circle
    # detections
    img = cv.medianBlur(gray, 37)
    # Finally, OpenCV built-in algorithm searching for circles. Arguments are a
    # bit tricky. The most useful are minDist (equals to 50 in this example)
    # and param{1,2}. First one represents distance between centers of detected
    # circles so we never have multiple circles in one place. However,
    # increasing this parameter too much may prevent detection of some circles.
    # Increasing param1 increases count of detected circles. Increasing param2
    # drops more false circles.
    circles = cv.HoughCircles(img, cv.HOUGH_GRADIENT,
                              1, 50, param1=120, param2=40)

    if not circles is None:
        circles = np.uint16(np.around(circles))
        # Filter the biggest circle, we don't want far signs to be detected
        # instead of close ones.
        max_r, max_i = 0, 0
        for i in range(len(circles[:, :, 2][0])):
            if circles[:, :, 2][0][i] > 50 and circles[:, :, 2][0][i] > max_r:
                max_i = i
                max_r = circles[:, :, 2][0][i]
        x, y, r = circles[:, :, :][0][max_i]
        # This check prevents program crash when trying to index list out of
        # its range. We actually cut a square with the whole circle inside.
        if y > r and x > r:
            square = frame[y-r:y+r, x-r:x+r]

            dominant_color = get_dominant_color(square, 2)
            if dominant_color[2] > 100:
                stop()
                # Stop sign is red, so we check if there is a lot of red color
                # in circle.
                print("STOP")
            elif dominant_color[0] > 80:
                # Other signs are blue.

                # Here we cut 3 zones from the circle, then count their
                # dominant color and finally compare.
                zone_0 = square[square.shape[0]*3//8:square.shape[0]
                                * 5//8, square.shape[1]*1//8:square.shape[1]*3//8]
                zone_0_color = get_dominant_color(zone_0, 1)

                zone_1 = square[square.shape[0]*1//8:square.shape[0]
                                * 3//8, square.shape[1]*3//8:square.shape[1]*5//8]
                zone_1_color = get_dominant_color(zone_1, 1)

                zone_2 = square[square.shape[0]*3//8:square.shape[0]
                                * 5//8, square.shape[1]*5//8:square.shape[1]*7//8]
                zone_2_color = get_dominant_color(zone_2, 1)

                if zone_1_color[2] < 60:
                    if sum(zone_0_color) > sum(zone_2_color):
                        turn_left()
                        time.sleep(0.5)
                        stop()
                        time.sleep(1)
                        forward()
                        time.sleep(1)
                        print("LEFT")
                    else:
                        turn_right()
                        time.sleep(0.5)
                        stop()
                        time.sleep(1)
                        forward()
                        time.sleep(1)
                        print("RIGHT")
                else:
                    if sum(zone_1_color) > sum(zone_0_color) and sum(zone_1_color) > sum(zone_2_color):
                        forward()
                        time.sleep(5)

                        print("FORWARD")
                    elif sum(zone_0_color) > sum(zone_2_color):
                        print("FORWARD AND LEFT")
                    else:
                        turn_right()
                        time.sleep(0.5)
                        stop()
                        time.sleep(1)
                        forward()
                        time.sleep(1)
                        print("RIGHT")

                        print("FORWARD AND RIGHT")
            else:
                print("N/A")

        # Draw all detected circles on the screen
        for i in circles[0, :]:
            cv.circle(frame, (i[0], i[1]), i[2], (0, 255, 0), 2)
            cv.circle(frame, (i[0], i[1]), 2, (0, 0, 255), 3)
    cv.imshow('camera', frame)


cv.destroyAllWindows()
cameraCapture.release()
GPIO.cleanup()
