import cv2, time, os
import numpy as np
from PIL import Image
import google_cloud_storage
from database import UserDatabase

gcs = google_cloud_storage.GoogleCloudStorage()


def get_usable_camera_id():
    """Find the first camera that is usable by the device
    :return: int
    """
    for i in range(4):
        if cv2.VideoCapture(i) is not None and cv2.VideoCapture(i).isOpened():
            return i


def show_video_capture():
    """For demonstration purpose, show camera, press Q to stop operation
    """
    video = cv2.VideoCapture(get_usable_camera_id(), cv2.CAP_DSHOW)
    video.set(3, 480)
    video.set(4, 480)
    

    while True:
        # Create a frame object
        check, frame = video.read()
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        cv2.imshow("Capturing" , gray)

        key = cv2.waitKey(1)

        if key == ord('q'):
            break

    # Shut down camera
    video.release()

    cv2.destroyAllWindows



def faceset_capture(id, name):
    """When run will start capturing images of faces on the camera, save in the /user_dataset folder
    Naming scheme is based on id
    :param id: id of the new user to capture face
    :param name: name of the new user to capture face
    :type id: string
    :type name: string
    :return: void
    """
    # list_of_users = read_user_dataset()

    # Start camera
    camera = cv2.VideoCapture(get_usable_camera_id(), cv2.CAP_DSHOW)

    # Use casecade identifier to detect frontal faces
    face_detector = cv2.CascadeClassifier('haarcascade_frontalface_default.xml')

    # Keep track of number of images captured
    count = 0

    while True:
        # Capture camera frame
        _,frame = camera.read()

        # Convert to grayscale
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

        faces = face_detector.detectMultiScale(gray, 1.3, 5)
        for (x,y,w,h) in faces:
            cv2.rectangle(frame, (x,y), (x+w, y+h), (255,0 ,0) , 2)
            count += 1
            file_name = "User."+str(id)+"."+str(name)+'.'+str(count)+".jpg"
            # cv2.imwrite("user_dataset/User."+str(id)+"."+str(name)+'.'+str(count)+".jpg", gray[y:y+h,x:x+w])
            cv2.imwrite("user_dataset/" + file_name, gray[y:y+h,x:x+w])
            # upload images to cloud
            gcs.upload_from_filename("user_dataset/" + file_name, file_name)

        # Display the  frame, with bounded rectangle on the person's face
        cv2.imshow('frame', frame)

        # To stop, press 'q' for at least 100ms or 50 images are taken reach 50
        if (cv2.waitKey(100) & 0xFF == ord('q')) or count > 20:
            break

    

    # Ends camera
    camera.release()
    cv2.destroyAllWindows()


# Train the faceset so it can be recognize

def train_faceset():
    """Will train all the face models and store it in trainer.yml
    :return: void
    """
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

        print("Training user of id "+ str(os.path.split(imagePath)[-1].split(".")[1]))

        id = int(os.path.split(imagePath)[-1].split(".")[1])

        # Get the face from the training images
        faces = detector.detectMultiScale(img_numpy)

        # Loop for each face, append to their respective ID
        for (x,y,w,h) in faces:

            # Add the image to face samples
            faceSamples.append(img_numpy[y:y+h,x:x+w])

            # Add the ID to IDs
            ids.append(id)
    print(np.array(ids))
    # Train the model using the faces and IDs
    recognizer.train(faceSamples, np.array(ids))

    # Save the model into trainer.yml
    recognizer.save('trainer/trainer.yml')


def face_recognition_start(id):
    """Start monitoring camera to find the the face of the user with the same ID, press Q to stop
        
    :param id: id of the user to be recognize
    :type id: string
    :return: True or False
    """
    gcs.download_trainer()

    # Get all users from MySQL Database
    users = UserDatabase()
    user_dict = users.get_all()
    print(user_dict)

    # Create Local Binary Patterns Histograms for face recognization
    recognizer = cv2.face.LBPHFaceRecognizer_create()

    # Load the trained mode
    recognizer.read('trainer.yml')

    # Load prebuilt model for Frontal Face
    cascadePath = "haarcascade_frontalface_default.xml"

    # Create classifier from prebuilt model
    faceCascade = cv2.CascadeClassifier(cascadePath)
    # Set the font style
    font = cv2.FONT_HERSHEY_SIMPLEX

    # Initialize and start the video frame capture
    cam = cv2.VideoCapture(get_usable_camera_id(), cv2.CAP_DSHOW)

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

            print(recognizer.predict(gray[y:y+h,x:x+w]))
            # Recognize the face belongs to which ID
            Id = recognizer.predict(gray[y:y+h,x:x+w])

            for user in user_dict:
                print(user['USER_ID'])
                print(Id)
                if(Id[0] == user['USER_ID']):
                    Id = user['name']
                    break
                else:
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

    return False