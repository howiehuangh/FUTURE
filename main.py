from os import device_encoding
import cv2
import numpy as np
import time
from datetime import datetime
import signal
import sys

from numpy.lib.function_base import _calculate_shapes

from utils.serv import HTTPcontrol
from utils.led_ctrl import LedStrip
from utils.modbus_ctrl_031022 import RelayCtrl
from utils.obsbot_ctrl import ObsbotCtrl, WebCam
from utils.gesture_recognizer import GestureRecognizer
from utils.pitch_analyzer import Pitch_Analyzer

import pyvirtualcam as vcam
import subprocess

from src.stream_analyzer import Stream_Analyzer



# Jacky add
global serialPortClose
CONFIDENCE_THRESHOLD = 0.2
NMS_THRESHOLD = 0.4
COLORS = [(0, 255, 255), (255, 255, 0), (0, 255, 0), (255, 0, 0)]

class_names = []
with open("coco_classes.txt", "r") as f:
    class_names = [cname.strip() for cname in f.readlines()]
    # print(class_names)


class Robot:
    def __init__(self):
        self.cameraCtrl = ObsbotCtrl()
        self.led_strip = LedStrip()
        self.relay = RelayCtrl()
        self.gestureRecognizer = GestureRecognizer()
        self.cam = WebCam(resolution=(1920, 1080), device_id=1)
        print(self.cam)
        self.pitch_analyze = Pitch_Analyzer()
        self.pitch_analyze._start()

        # self.audio_deive = None
        # self.ear = Stream_Analyzer(
        #             device = self.audio_deive,        # Pyaudio (portaudio) device index, defaults to first mic input
        #             rate   = None,               # Audio samplerate, None uses the default source settings
        #             FFT_window_size_ms  = 60,    # Window size used for the FFT transform
        #             updates_per_second  = 1000,  # How often to read the audio stream for new data
        #             smoothing_length_ms = 50,    # Apply some temporal smoothing to reduce noisy features
        #             n_frequency_bins = 400, # The FFT features are grouped in bins
        #             visualize = 0,               # Visualize the FFT features with PyGame
        #             verbose   = False,    # Print running statistics (latency, fps, ...)
        #             height    = 450,     # Height, in pixels, of the visualizer window,
        #             window_ratio = '24/9'  # Float ratio of the visualizer window. e.g. 24/9
        #             )


        # self.dt = 0.05 # pause time between frames
        # self.cam = cv2.VideoCapture(2)
        # self.cam.set(cv2.CAP_PROP_FPS,30)
        # self.cam.set(cv2.CAP_PROP_FRAME_WIDTH,1920)
        # self.cam.set(cv2.CAP_PROP_FRAME_HEIGHT,1080)
        #self.videoWriter = cv2.VideoWriter('oto_other.avi', cv2.cv.CV_FOURCC('M', 'J', 'P', 'G'), fps, size)

        #self.vcam_obj = vcam.Camera(width=1920,height=1080,fps=30)
        self.stime = time.time()
        self.gesture = None
        self.count_down = None
        self.freq_to_color = False

        # Jacky added
        self.ai_cam_start = False
        self.ai_cam_entered = False
        self.detected_object = []

        net = cv2.dnn.readNet("weights/yolov4.weights", "weights/yolov4.cfg")
        net.setPreferableBackend(cv2.dnn.DNN_BACKEND_CUDA)
        net.setPreferableTarget(cv2.dnn.DNN_TARGET_CUDA_FP16)

        self.model = cv2.dnn_DetectionModel(net)
        self.model.setInputParams(size=(416, 416), scale=1 / 255, swapRB=True)

        # Jacky added
        # self.move_pattern = ['#9cb600', '#c9ac00', '#ed4400', '#9cb600', '#c9ac00', '#ed4400']
        self.move_pattern = ['#9cb600', '#c9ac00', '#ed4400']
        self.current_pattern = []
        self.move = False

        self.cam.start()

    # self.
    # ptz camera
    # modbus board
    # agv
    # no need
    def run(self):
        run_end = True
        fps = 60  # How often to update the FFT features + display
        last_update = time.time()

        while run_end:
            frame = self.cam.getframe()
            if frame is None:
                print("failed to grab frame")
                run_end = False
                break

            self.img_ex = cv2.resize(frame, (1280, 752))

            image = frame.copy()
            ########################################
            ## check to frequency to color
            ########################################
            if self.pitch_analyze.pitch_result is not None:
                if self.freq_to_color == True:
                    color_code = self.pitch_analyze.frequency_to_color()
                    print("color code: ", color_code, "freq:", self.pitch_analyze.pitch_result, "volume:", self.pitch_analyze.volume )
                else:
                    color_code = None
            if color_code is not None and (float(self.pitch_analyze.volume) > self.pitch_analyze.volume_threadhold):
                self.led_strip.setColor_with_timer(color_code)
                print("color code: ", color_code, "freq:", self.pitch_analyze.pitch_result, "volume:", self.pitch_analyze.volume)

                # print("color code: ", color_code)
                if color_code in self.pitch_analyze.pattern and len(self.pitch_analyze.current_pattern) < len(
                        self.pitch_analyze.move_front_pattern):
                    if len(self.pitch_analyze.current_pattern) > 0:
                        if color_code != self.pitch_analyze.current_pattern[-1]:
                            self.pitch_analyze.current_pattern.append(color_code)
                    else:
                        self.pitch_analyze.current_pattern.append(color_code)
                    print("pitch_analyze.current_pattern: ", self.pitch_analyze.current_pattern)
                    if len(self.pitch_analyze.current_pattern) == len(self.pitch_analyze.move_front_pattern):
                        if self.pitch_analyze.current_pattern == self.pitch_analyze.move_front_pattern:
                            print("Move Front.......")
                            subprocess.call(["python", "piano_move.py", "forward"], shell=True)
                        elif self.pitch_analyze.current_pattern == self.pitch_analyze.move_back_pattern:
                            print("Move Backward.......")
                            subprocess.call(["python", "piano_move.py", "backward"], shell=True)
                        else:
                            print("Pattern not match")
                        self.pitch_analyze.current_pattern.clear()
                        time.sleep(2)

            # if (time.time() - last_update) > (1./fps):
            #     last_update = time.time()
            #     if self.freq_to_color == True:
            #         peak_frequency = self.ear.get_audio_features()
            #         color_code = self.ear.frequency_to_color((500,2100))
            #         if color_code is not None:
            #             self.led_strip.setColor_with_timer(color_code,timer=0)
            #             print('color_code:',color_code)

            ########################################
            # check to display movice recording...
            ########################################
            if self.cam.kill_display == True:
                self.cam.kill_display = False
                cv2.destroyWindow("Movie Recording...")
                #cmd_mov = 'C:\Future\software\{}'.format(self.cam.mov_name)
                subprocess.Popen([r'C:\Future\software\{}'.format(mov_name)], shell=True)

                #time.sleep(2)
            if self.cam.record_status == 'on':
                cv2.namedWindow("Movie Recording...", cv2.WIself.camNDOW_FULLSCREEN)
                # cv2.setWindowProperty("Movie Recording...",cv2.WND_PROP_TOPMOST,1)
                # cv2.moveWindow("Movie Recording...",0,0)
                cv2.imshow('Movie Recording...', frame)

            ########################################
            # check gesture
            ########################################
            if self.count_down is None:
                self.gesture = self.gestureRecognizer.checkGesture(image)
                # cv2.imshow('Snap', frame)
                # gesture = None
            if self.gesture is not None or self.count_down is not None:
                if self.count_down == None:
                    # start to down down to snap
                    print('gesture:', self.gesture)
                    self.count_down = 5
                    self.stime = time.time()
                    cv2.namedWindow("Snap", cv2.WINDOW_FULLSCREEN)
                    cv2.setWindowProperty("Snap", cv2.WND_PROP_TOPMOST, 1)
                    cv2.setWindowProperty("Snap", cv2.WINDOW_FULLSCREEN, 1)
                    # cv2.moveWindow("Snap",0,0)
                    cv2.putText(frame, str(self.count_down), (250, 80), cv2.FONT_HERSHEY_SIMPLEX, 2, (0, 0, 255), 3, cv2.LINE_AA)
                    cv2.imshow('Snap', frame)
                    time.sleep(0.05)
                elif self.count_down <= 0:
                    pass
                    # snap
                else:
                    ellaped_time = time.time() - self.stime
                    self.count_down = 5 - int(ellaped_time)
                    if self.count_down == 0:
                        str_now = datetime.now().strftime("%Y%m%d%H%M%S")
                        img_name = "img_{}.jpg".format(str_now)
                        cv2.imshow('Snap', frame)
                        cv2.imwrite(img_name, frame)
                        cv2.waitKey(1)
                        time.sleep(2)
                        cv2.destroyAllWindows()
                        self.count_down = None
                    else:
                        cv2.namedWindow("Snap", cv2.WINDOW_FULLSCREEN)
                        cv2.moveWindow("Snap", 0, 0)
                        cv2.putText(frame, str(self.count_down), (250, 80), cv2.FONT_HERSHEY_SIMPLEX, 2, (0, 0, 255), 3, cv2.LINE_AA)
                        cv2.imshow('Snap', frame)

            if self.ai_cam_start:
                self.ai_cam_entered = True
                cv2.namedWindow('AI detections', cv2.WINDOW_NORMAL)
                start = time.time()
                classes, scores, boxes = self.model.detect(image, CONFIDENCE_THRESHOLD, NMS_THRESHOLD)
                end = time.time()

                self.detected_object.clear()
                for classid in classes:
                    self.detected_object.append(class_names[classid[0]])

                for (classid, score, box) in zip(classes, scores, boxes):
                    color = COLORS[int(classid) % len(COLORS)]
                    label = "%s : %f" % (class_names[classid[0]], score)

                    cv2.rectangle(image, box, color, 2)
                    cv2.putText(image, label, (box[0], box[1] - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2)

                fps_label = "FPS: %.2f" % (1 / (end - start))
                cv2.putText(image, fps_label, (0, 25), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 0), 2)
                cv2.imshow("AI detections", image)
                cv2.setWindowProperty("AI detections", cv2.WND_PROP_TOPMOST, 1)
            elif not self.ai_cam_start and self.ai_cam_entered:
                cv2.destroyWindow("AI detections")
                self.detected_object.clear()

            key = cv2.waitKey(100)
            if key == ord('q'):
                break

def exit_gracefully(signum, frame):
    # restore the original signal handler as otherwise evil things will happen
    # in raw_input when CTRL+C is pressed, and our signal handler is not re-entrant
    signal.signal(signal.SIGINT, original_sigint)
    try:
        if input("\nReally quit? (y/n)> ").lower().startswith('y'):
            print("Checker",serialPortClose)
            serialPortClose.close()
            print("Checker",serialPortClose)
            os._exit(1)

    except KeyboardInterrupt:
        print("Ok ok, quitting")
        print("Checker",serialPortClose)
        serialPortClose.close()
        print("Checker",serialPortClose)
        os._exit(1)

    # restore the exit gracefully handler here    
    signal.signal(signal.SIGINT, exit_gracefully)


if __name__ == "__main__":
    robot = Robot()
    serialPortClose = robot.led_strip.serial_obj
    print("Checker",serialPortClose)
    original_sigint = signal.getsignal(signal.SIGINT)
    signal.signal(signal.SIGINT, exit_gracefully)

    # http_control = HTTPcontrol(robot=robot)
    # http_control.start()
    agv_control = HTTPcontrol(robot=robot , port=8080)
    agv_control.start()

    robot.run()
    print('end')
