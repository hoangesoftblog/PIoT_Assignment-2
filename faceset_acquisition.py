import cv2, time

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

def capture_faceset(id):
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


# show_video_capture()
# capture_faceset('0001')

