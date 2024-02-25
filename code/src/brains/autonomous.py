from . import base
import cv2 as cv
import time


class Config(base.Config):
    pass


class Brain(base.Brain):

    """The autonomous Brain object, drives the vehicle autonomously based on information gathered by the sensors"""

    def __init__(self, config: Config, *arg):
        super().__init__(config, *arg)

        # load the face detection model
        self.face_detect = cv.CascadeClassifier("/home/pi/Desktop/HackIllinois2024/code/src/brains/haarcascade_frontalface_default.xml")
        self.image_counter = 0
        cv.namedWindow("result", cv.WINDOW_NORMAL)
        cv.resizeWindow('result', 64, 64)
    
    def DetectFace(self, image):
        # gray scale
        
        gray_image = cv.cvtColor(image, cv.COLOR_BGR2GRAY)
        # check result
        face_result = self.face_detect.detectMultiScale(gray_image, scaleFactor=1.3, minNeighbors=5)
        # drawframe
        for x, y, w, h in face_result:
            cv.rectangle(image, (x, y), (x+w, y+h), (0, 255, 0), 2)

        cv.imshow("result", image)
        cv.waitKey(2)

        return face_result


    def logic(self):
        """If anything is detected by the distance_sensors, stop the car"""
        image_w = self.camera.image_array.shape[1]
        center = image_w // 2
        hori_p = 0
        w = 0
    
        # got_face = False
        # print(self.camera.image_array.shape)
        
        # getting horizontal position of the top left and width of the box
        image = cv.cvtColor(self.camera.image_array, cv.COLOR_RGB2BGR)
        face_pos = self.DetectFace(image)

        if len(face_pos) != 0:
            # got_face = True
            hori_p, _ , w, _ = face_pos[0]
            self.image_counter %= 10
            image_name = f"captured_image_{self.image_counter}.jpg"
            cv.imwrite(image_name, image)
            print(f"Image saved: {image_name}")
            self.image_counter += 1


        # print(hori_p,w)
        
        if hori_p and w:
            # if the face is on the left
            hori_p = hori_p + w // 2
            if hori_p < center - 25:
                start_time = time.time()

                # Calculate the horizontal distance between face center and image center
                horizontal_distance = abs(hori_p - (center - 10))
       
                while time.time() - start_time < abs(horizontal_distance / image_w):
                    self.vehicle.pivot_left(0.55)
                
            # if the face is on the right
            elif hori_p > center + 25:
                start_time = time.time()

                # Calculate the horizontal distance between face center and image center
                horizontal_distance = abs(hori_p - (center - 10))

                while time.time() - start_time < abs(horizontal_distance / image_w):
                    self.vehicle.pivot_right(0.55)
        
            else:
                start_time = time.time()
                while time.time() - start_time < 1:
                    self.vehicle.drive_forward(1)
                start_time = time.time()
                while time.time() - start_time < 0.1:
                    self.vehicle.drive_backward(0.6)

        self.vehicle.stop()
        

