import tkinter as tk
import PIL
from PIL import Image, ImageTk
import cv2
import numpy as np
import google_cloud_storage
from database import BookingDatabase, LoginDatabase, UserDatabase, EmployeesDatabase, IssuesDatabase
import socket_communication
import json
import datetime
import camera
import os

gcs = google_cloud_storage.GoogleCloudStorage()


class AgentPiApp(tk.Tk):
    """Agent PI GUI built with tkinter, is a subclass of the Tk class, a window, used for customers to login with their credentials
    or face to access the car, for engineer to show their QR code to access the car
    """
    def __init__(self, car_id):
        tk.Tk.__init__(self)
        self.car_id = car_id
        print("Agent for car of id " + str(self.car_id) + " is created")
        self.attributes('-fullscreen', False)  

        # To rename the title of the window
        self.title("Car Sharing System - By Big City Bois")
        # self.geometry('960x540')
        
        # self.window.rowconfigure(0, weight=1)
        self.columnconfigure(0, weight=1)

        self._frame = None
        self.switch_frame(LoginPage)

    def is_access_allowed(self, user_id):
        """Return True or False if the user is allowed to access the car or not
        Parameters
        ----------
        user_id
            The Id of the user trying to access the car
        """
        ### DATABASE CODE GOES HERE
        return False


    def get_accessible_user_id(self):
        """Return the user id that is allowed to access the car, at current time
        
        """
        ### DATABASE CODE GOES HERE
        return 1


    def switch_frame(self, frame_class):
        """To switch the main window frame to another
        
        Parameters
        ----------
        frame_class
            The frame subclass to switch to
        """
        new_frame = frame_class(self)
        if self._frame is not None:
            self._frame.destroy()
        self._frame = new_frame
        self._frame.pack()

class LoginPage(tk.Frame):
    """Login Page frame, to show the options available to the users
    """
    def __init__(self, master):
        """Initializing the login page frame
        """
        tk.Frame.__init__(self, master)
        self.master = master

        # Set the UI    
        self.welcome = tk.Label(self, text = "Welcome!", font=("Arial Bold", 50)).grid(row = 0, ipady = 80)

        self.login_frame = tk.LabelFrame(self, width = 50)
        self.login_frame.grid(row = 1)

        label_username = tk.Label(self.login_frame, text = "Username: \t", font=("Arial Bold", 30)).grid(row = 1, column = 0, pady = 5)
        self.entry_username = tk.Entry(self.login_frame, width = 20, font=("Arial Bold", 30))
        self.entry_username.grid(row = 1, column = 1, pady = 5)
        label_password = tk.Label(self.login_frame, text = "Password: \t", font=("Arial Bold", 30)).grid(row = 2, column = 0, pady = 5)
        self.entry_password = tk.Entry(self.login_frame, width = 20, font=("Arial Bold", 30), show="*")
        self.entry_password.grid(row = 2, column = 1, pady = 5)
        self.bt_login = tk.Button(self.login_frame, text = "Login", font=("Arial Bold", 30), fg = "red", command = self.login_bt_pressed)
        self.bt_login.grid(row = 3, columnspan = 2, pady = 15)

        self.bt_login_face = tk.Button(self,width = 30,  text = "Login with facial recognition", font=("Arial Bold", 30), fg = "red", command=lambda: master.switch_frame(FacePage))
        self.bt_login_face.grid(row = 3, pady = 60)
        self.bt_login_qr = tk.Button(self, width = 30 , text = "Engineer QR", command=lambda: master.switch_frame(QrPage), font=("Arial Bold", 30), fg = "red")
        self.bt_login_qr.grid(row = 4)


    def login_bt_pressed(self):
        """This is the event that attached to bt_login"""
        username = self.entry_username.get()
        password = self.entry_password.get()
        print("Username: " + username)
        print("Password: " + password)

        ### IDENTIFICATION & SOCKET CODE GOES HERE
        # if username == "Hieu" and password == "Hieu":
        #     self.master.switch_frame(AccessGranted)
        # else: 
        #     self.master.switch_frame(AccessDenied)
        client_socket = socket_communication.Socket_Client()

        data = {}
        data[LoginDatabase.PASSWORD] = password
        data[LoginDatabase.USERNAME] = username
        data[BookingDatabase.CAR_ID] = self.master.car_id

        client_socket.send_message("Normal".encode())
        client_socket.receive_message()
        client_socket.send_message(json.dumps(data).encode())
        client_socket.receive_message()
        return_message = client_socket.receive_message()

        print("Return message:", return_message)    

        if return_message == "Correct":
            self.master.switch_frame(AccessGranted)
        else:
            self.master.switch_frame(AccessDenied)

        # return (self.entry_username.get(),self.entry_password.get())

class AccessGranted(tk.Frame):
    """Showing the screen so users knows that they have successfully identified as the user of the car
    """
    def __init__(self, master):
        """Create the access granted frame
        
        """
        tk.Frame.__init__(self, master)

        self.access_granted = tk.Label(self, text = "Access Granted!", font=("Arial Bold", 100), fg = "green", pady = 80).pack()
        tk.Button(self, text = "Back", font=("Arial Bold", 30), command=lambda: master.switch_frame(LoginPage)).pack()

class AccessDenied(tk.Frame):
    """Showing the screen so users knows that they been refused to access the car
    """
    def __init__(self, master):
        """Create the access denied frame
        
        """
        tk.Frame.__init__(self, master)
        self.access_granted = tk.Label(self, text = "Access Denied!", font=("Arial Bold", 100), fg = "red", pady = 80).pack()
        tk.Button(self, text = "Back", font=("Arial Bold", 30), command=lambda: master.switch_frame(LoginPage)).pack()


class FacePage(tk.Frame):
    """ The Class to manage the facial recognition frame
    
    """
    def __init__(self,master):
        """Initializing the facial recognition frame
        
        """
        tk.Frame.__init__(self, master)
        self.master = master
        
        # Get all users from MySQL Database
        login_db = LoginDatabase()
        # self.user_dict = users.get_all()
        # print(self.user_dict)

        # Download all neccessary files if needed
        if not os.path.exists("trainer.yml"):
            gcs.download_trainer()

        # Create Face Detector
        self.faceCascade = cv2.CascadeClassifier("haarcascade_frontalface_default.xml")

        # Create Local Binary Patterns Histograms (LBPH) Face Recognizer with pre-trained weights
        self.recognizer = cv2.face.LBPHFaceRecognizer_create()
        self.recognizer.read('trainer.yml')

        # Create a VideoCamera object
        self.vid = ApVideoCapture()

        # Elements on the UI
        self.canvas = tk.Canvas(self, width = self.vid.width, height=self.vid.height)
        self.canvas.pack()
        tk.Button(self, text="Back", font=("Arial Bold", 30), command=lambda: master.switch_frame(LoginPage)).pack()
        
        # Since we need to check if a same face is detect for 5 times
        # identification_count counts how many times it has been appeared already
        # id is for the User ID detected
        self.identification_count = 0
        self.ID = None

        # Start the function to update UI
        self.update()


    def update(self):
        """Update the canvas showing the camera feed on the frame
        
        """
        # Get frame from video source:
        ret, frame = self.vid.read()

        if ret:
            # Convert the captured frame into grayscale
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            gray = cv2.equalizeHist(gray)

            # Get all faces from the video frame
            faces = self.faceCascade.detectMultiScale(gray, 1.2,5)

            # For each face in faces
            for (x, y, w, h) in faces:
                # Create rectangle around the face
                cv2.rectangle(frame, (x-20,y-20), (x+w+20,y+h+20), (0,255,0), 4)

                # Recognize the face belongs to which ID
                predicted_ID, distance = self.recognizer.predict(gray[y:y+h,x:x+w])
                print(predicted_ID, distance)

                # # Put text describe who is in the picture
                # cv2.rectangle(frame, (x - 22, y - 90), (x + w + 22, y - 22), (0, 255, 0), -1)
                # cv2.putText(frame, str(predicted_ID), (x, y - 40), cv2.FONT_HERSHEY_SIMPLEX, 2, (255, 255, 255), 3)

                # # # Start using predicted value to send data
                if predicted_ID == self.ID:
                    if self.identification_count < 5:
                        self.identification_count += 1
                    else:
                        self.identification_count = 0
                        # Start sending data to server and receive it
                        data = {BookingDatabase.USER_ID: self.ID, BookingDatabase.CAR_ID: self.master.car_id}

                        client_socket = socket_communication.Socket_Client()
                        client_socket.send_message("Facial".encode())
                        client_socket.receive_message()
                        client_socket.send_message(json.dumps(data).encode())
                        return_message = client_socket.receive_message()
                        print("Return message:", return_message)

                        if return_message == "Correct":
                            self.master.switch_frame(AccessGranted)
                            return
                        else:
                            self.master.switch_frame(AccessDenied)
                            return
                else:
                    self.ID = predicted_ID
                    self.identification_count = 0
                
            # Put the frame into the UI
            try:                
                self.photo = PIL.ImageTk.PhotoImage(image = PIL.Image.fromarray(frame))
                self.canvas.create_image(0, 0, image = self.photo, anchor = tk.NW)
            except Exception as e:
                print(e)

        self.after(50, self.update)


class QrPage(tk.Frame):
    """ The Class to manage the QR recognition frame
    ...
    """
    def __init__(self,master):
        """Initializing the qr recognition frame
        
        """
        tk.Frame.__init__(self, master)
        self.master = master

        # Create VideoCamera object
        self.vid = ApVideoCapture()
        # Create a QR Detector
        self.detector = cv2.QRCodeDetector()

        # Declare elements on the UI
        self.canvas = tk.Canvas(self, width = self.vid.width, height = self.vid.height)
        self.canvas.pack()
        tk.Button(self, text = "Back", font=("Arial Bold", 30), command=lambda: master.switch_frame(LoginPage)).pack()
        
        # Start update the UI with camera
        self.update()


    def update(self):
        """Update the canvas showing the camera feed on the frame.\n
        Multiple QR codes are not supported
        
        """
        # Get frame from video source:
        ret, frame = self.vid.read()

        if ret:
            data, bbox, _ = self.detector.detectAndDecode(frame)
            
            if bbox is not None:
                # Draw borders for illustration
                for i in range(len(bbox)):
                    cv2.line(frame, tuple(bbox[i][0]), tuple(bbox[(i+1) % len(bbox)][0]), color=(255, 0, 0), thickness=2)

            if data:
                data = {IssuesDatabase.ENGINEER_ID: data, Iss.CAR_ID: self.master.car_id}

                client_socket = socket_communication.Socket_Client()
                client_socket.send_message("QR".encode())
                client_socket.receive_message()
                client_socket.send_message(json.dumps(data).encode())
                return_message = client_socket.receive_message()
                print("Return message:", return_message)

                if return_message == "Correct":
                    self.master.switch_frame(AccessGranted)
                    return
                else:
                    self.master.switch_frame(AccessDenied)
                    return
                # print("[+] QR Code detected, data:", data)

            self.photo = PIL.ImageTk.PhotoImage(image = PIL.Image.fromarray(frame))
            self.canvas.create_image(0, 0, image = self.photo, anchor = tk.NW)


        self.after(15, self.update)



class ApVideoCapture:
    """ Provide video capture to the other frames
    
    """
    def __init__(self, video_source = 0):
        """ Turn on the camera
        
        Parameters
        ----------
        video_source
            The index of the camera to use, defaults to 0
        """
        self.vid = cv2.VideoCapture(video_source)
        if not self.vid.isOpened():
            raise ValueError("Unable to open video source", video_source)


        # Get video source width and height
        self.width = self.vid.get(cv2.CAP_PROP_FRAME_WIDTH)
        self.height = self.vid.get(cv2.CAP_PROP_FRAME_HEIGHT)


    def __del__(self):
        """ Turn off the camera
        """
        self.vid.release()

    def read(self):
        """ Get the frame that the camera captured as a tuple of (ret, frame)
        """
        if self.vid.isOpened():
            ret, frame = self.vid.read()
            if ret:
                return (ret, cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
            else:
                return (ret, None)
        else:
            return (ret, None)


if __name__ == "__main__":
    app = AgentPiApp(3)
    app.mainloop()  