import cv2, time, os
import numpy as np
from PIL import Image

# For demonstration purpose
"""For demonstration purpose 
"""

def show_video_capture():
    video = cv2.VideoCapture(0)
    video.set(3, 480)
    video.set(4, 480)
    

    while True:
        # Create a frame object
        check, frame = video.read()

        # print(check)
        # print(frame) #Represent image with matrices

        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        cv2.imshow("Capturing" , gray)

        key = cv2.waitKey(1)

        if key == ord('q'):
            break

    # Shut down camera
    video.release()

    cv2.destroyAllWindows


"""When run will start capturing images of faces on the camera, save in the /user_dataset folder
Naming scheme is based on id
"""
def faceset_capture(id):
    # Start camera
    camera = cv2.VideoCapture(0)

    # Use casecade identifier to detect frontal faces
    face_detector = cv2.CascadeClassifier('haarcascade_frontalface_default.xml')

    # Keep track of number of faces
    count = 0

    # Start looping
    while True:
        # Capture camera frame
        _,frame = camera.read()

        # Convert to grayscale
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

        faces = face_detector.detectMultiScale(gray, 1.3, 5)

        for (x,y,w,h) in faces:
            cv2.rectangle(frame, (x,y), (x+w, y+h), (255,0 ,0) , 2)

            count += 1

            cv2.imwrite("user_dataset/User."+str(id)+"."+str(count)+".jpg", gray[y:y+h,x:x+w])

            # Display the  frame, with bounded rectangle on the person's face
            cv2.imshow('frame', frame)

        
        # To stop taking video, press 'q' for at least 100ms
        if cv2.waitKey(100) & 0xFF == ord('q'):
            break

        # If image taken reach 50, stop taking video
        elif count>50:
            break

    # Ends camera
    camera.release()

    cv2.destroyAllWindows


# Train the faceset so it can be recognize
def train_faceset(id):
    # Create Local Binary Patterns Histograms for face recognization
    recognizer = cv2.face.LBPHFaceRecognizer_create()

    # Using prebuilt frontal face training model, for face detection
    detector = cv2.CascadeClassifier("haarcascade_frontalface_default.xml")

    # Get all file path
    imagePaths = [os.path.join('user_dataset',f) for f in os.listdir('user_dataset')] 
    
    # Initialize empty face sample
    faceSamples=[]
    
    # Initialize empty id
    ids = []

        # Loop all the file path
    for imagePath in imagePaths:

        # Get the image and convert it to grayscale
        PIL_img = Image.open(imagePath).convert('L')

        # PIL image to numpy array
        img_numpy = np.array(PIL_img,'uint8')

        id = int(os.path.split(imagePath)[-1].split(".")[1])
        print(id)

        # Get the face from the training images
        faces = detector.detectMultiScale(img_numpy)

        # Loop for each face, append to their respective ID
        for (x,y,w,h) in faces:

            # Add the image to face samples
            faceSamples.append(img_numpy[y:y+h,x:x+w])

            # Add the ID to IDs
            ids.append(id)

    # Train the model using the faces and IDs
    recognizer.train(faceSamples, np.array(ids))

    # Save the model into trainer.yml
    recognizer.save('trainer/trainer.yml')

def face_recognition_start(id):
    # Create Local Binary Patterns Histograms for face recognization
    recognizer = cv2.face.LBPHFaceRecognizer_create()

    # Load the trained mode
    recognizer.read('trainer/trainer.yml')

    # Load prebuilt model for Frontal Face
    cascadePath = "haarcascade_frontalface_default.xml"

    # Create classifier from prebuilt model
    faceCascade = cv2.CascadeClassifier(cascadePath)
    # Set the font style
    font = cv2.FONT_HERSHEY_SIMPLEX

    # Initialize and start the video frame capture
    cam = cv2.VideoCapture(0)

    # Loop
    while True:
        # Read the video frame
        ret, im =cam.read()

        # Convert the captured frame into grayscale
        gray = cv2.cvtColor(im,cv2.COLOR_BGR2GRAY)

        # Get all face from the video frame
        faces = faceCascade.detectMultiScale(gray, 1.2,5)

        # For each face in faces
        for(x,y,w,h) in faces:

            # Create rectangle around the face
            cv2.rectangle(im, (x-20,y-20), (x+w+20,y+h+20), (0,255,0), 4)

            # Recognize the face belongs to which ID
            Id = recognizer.predict(gray[y:y+h,x:x+w])

            # Check the ID if exist 
            if(Id[0] == 1):
                Id = "Hieu"
            #If not exist, then it is Unknown
            elif(Id[0] == 2):
                Id = "Uyen"
            else:
                print(Id)
                Id = "Unknown"

            # Put text describe who is in the picture
            cv2.rectangle(im, (x-22,y-90), (x+w+22, y-22), (0,255,0), -1)
            cv2.putText(im, str(Id), (x,y-40), font, 2, (255,255,255), 3)

        # Display the video frame with the bounded rectangle
        cv2.imshow('im',im) 

        # If 'q' is pressed, close program
        if cv2.waitKey(10) & 0xFF == ord('q'):
            break

    # Stop the camera
    cam.release()

    # Close all windows
    cv2.destroyAllWindows()




# show_video_capture()
# faceset_capture('0002')
train_faceset('0001')
face_recognition_start('0001')