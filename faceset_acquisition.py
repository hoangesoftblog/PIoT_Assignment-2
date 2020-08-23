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



# show_video_capture()
# faceset_capture('0001')
train_faceset('0001')