import numpy as np
import cv2
import os
import argparse
from datetime import datetime
import shutil
from shutil import copytree, ignore_patterns
import serial
import re
from PIL import Image
import base64
import requests

from scipy.spatial import distance
from imutils import face_utils
import imutils
import dlib
import cv2
import pygame
import time
import RPi.GPIO as GPIO
import Adafruit_CharLCD as LCD



url = 'http://iotgecko.com/IOTImgAdd.aspx?id=aduboakyenk@gmail.com&pass=9282'

GPIO.setmode(GPIO.BCM)

val = 1

lcd_rs        = 21  # Note this might need to be changed to 21 for older revision Pi's.
lcd_en        = 20
lcd_d4        = 12
lcd_d5        = 7
lcd_d6        = 8
lcd_d7        = 9

lcd_columns = 16
lcd_rows    = 2

reset = 10
GPIO.setup(reset,GPIO.IN)

lcd = LCD.Adafruit_CharLCD(lcd_rs, lcd_en, lcd_d4, lcd_d5, lcd_d6, lcd_d7,
                           lcd_columns, lcd_rows)


def check_connectivity():
    try:
        ret, frame = camera.read()
        print ('sending sample image')
        t1 = datetime.now()
        cv2.imwrite("pic2.jpeg", frame)
        with open('pic2.jpeg', 'rb') as f:
            en = base64.b64encode(f.read())
        data ={'img':en}
        r = requests.post(url, data= data)
        res = r.text
        print(res)
        print(type(res))
        if res.find("True") > 0 or res.find("true") > 0:
            print('true')
            return True
        elif res.find("Error") > 0 or res.find("error") > 0: 
            print('flase')
            return False
    except:
        return False

def send_iot_data():
    try:
        x = 0
        for x in range(10):
            ret, frame = camera.read()
            cv2.imwrite("pic2.jpeg", frame)
        print ('sending sample image')
        with open('pic2.jpeg', 'rb') as f:
            en = base64.b64encode(f.read())
        data = {'img':en}
        r = requests.post(url, data= data)
        res = r.text
        print(res)
        if res.find("True"):
            return True
        elif res.find("Error"):
            return False
    except:
        return False

def eye_aspect_ratio(eye):
        A = distance.euclidean(eye[1], eye[5])
        B = distance.euclidean(eye[2], eye[4])
        C = distance.euclidean(eye[0], eye[3])
        ear = (A + B) / (2.0 * C)
        return ear


while True:
                lcd.clear()
                lcd.message('     Driver    \n   Drowsiness')
                time.sleep(3)
                lcd.clear()
                lcd.message(' Detection with \n IoT Monitoring')
                time.sleep(3)
                main = True
                print('Searching for Camera')
                lcd.clear()
                lcd.message('Searching for\nCamera...')
                time.sleep(1)

                camera=cv2.VideoCapture(0)

                if not camera.isOpened():
                        main = False
                        print ("can't open the camera")
                        lcd.clear()
                        lcd.message('Error:Camera not\nFound')
                        time.sleep(2)
                        lcd.clear()
                        lcd.message('Connect Camera &\npress reset')
                        while GPIO.input(reset) == True:
                            main = False
                            None
                else:
                        main = True
                        print ("camera found")
                        lcd.clear()
                        lcd.message('Found Camera!')
                        time.sleep(2)

                if main:
                    print('connecting to internet')
                    lcd.clear()
                    lcd.message('Connecting to \nInternet....')
                    time.sleep(1)
                    t1 = datetime.now()
                    while not check_connectivity() :
                            t2 = datetime.now()
                            delta = t2 - t1
                            time_elapse = delta.total_seconds()
                            if time_elapse > 10:
                                lcd.clear()
                                lcd.message('Unable to \nConnect...')
                                print ("error check you internet connection")
                                time.sleep(2)
                                main = False
                                while GPIO.input(reset) == True:
                                    lcd.clear()
                                    lcd.message('Press Reset to\nRestart')
                                    time.sleep(0.5)
                                break
                            else:
                                main = True
                                
                lcd.clear()
                lcd.message('Connected!')
                camera.release()              
                thresh = 0.25
                frame_check = 20
                detect = dlib.get_frontal_face_detector()
                predict = dlib.shape_predictor("/home/pi/Drowsiness_Detection/shape_predictor_68_face_landmarks.dat")
                (lStart, lEnd) = face_utils.FACIAL_LANDMARKS_68_IDXS["left_eye"]
                (rStart, rEnd) = face_utils.FACIAL_LANDMARKS_68_IDXS["right_eye"]
                camera=cv2.VideoCapture(0)
                flag=0
                lcd.clear()
                lcd.message('Monitoring...')
                time.sleep(3)
                lcd.clear()
                                
                while main == True:        
                        lcd.clear()
                        lcd.message('Monitoring...')
                        ret, frame=camera.read()
                        frame = imutils.resize(frame, width=450)
                        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                        subjects = detect(gray, 0)
                        for subject in subjects:
                                lcd.clear()
                                lcd.message('Monitoring...')
                                shape = predict(gray, subject)
                                shape = face_utils.shape_to_np(shape)#converting to NumPy Array
                                leftEye = shape[lStart:lEnd]
                                rightEye = shape[rStart:rEnd]
                                leftEAR = eye_aspect_ratio(leftEye)
                                rightEAR = eye_aspect_ratio(rightEye)
                                ear = (leftEAR + rightEAR) / 2.0
                                leftEyeHull = cv2.convexHull(leftEye)
                                rightEyeHull = cv2.convexHull(rightEye)
                                cv2.drawContours(frame, [leftEyeHull], -1, (0, 255, 0), 1)
                                cv2.drawContours(frame, [rightEyeHull], -1, (0, 255, 0), 1)
                                if ear < thresh:
                                        flag += 1
                                        print (flag)
                                        if flag >= frame_check:
                                                cv2.putText(frame, "****************ALERT!****************", (10, 30),
                                                        cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
                                                cv2.putText(frame, "****************ALERT!****************", (10,325),
                                                        cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
                                                print ("Drowsy")
                                                send_iot_data()
                                                lcd.clear()
                                                lcd.message('CANH BAO!!!! \nHay chu y...')       
                                                pygame.mixer.init()
                                                pygame.mixer.music.load("/home/pi/Drowsiness_Detection/alert.mp3")
                                                pygame.mixer.music.play()
                                                while pygame.mixer.music.get_busy() == True:
                                                        continue
                                else:
                                        flag = 0
                                
                        cv2.imshow("Frame", frame)
                        key = cv2.waitKey(1) & 0xFF
                        if key == ord("q"):
                                break
                cv2.destroyAllWindows()
                camera.stop()
