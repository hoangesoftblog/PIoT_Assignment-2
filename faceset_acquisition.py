import cv2, time




def show_video_capture():
    video = cv2.VideoCapture(0)

    while True:
        # Create a frame object
        check, frame = video.read()

        print(check)
        print(frame) #Represent image with matrices

        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        cv2.imshow("Capturing" , gray)

        key = cv2.waitKey(1)

        if key == ord('q'):
            break

    # Shut down camera
    video.release()

    cv2.destroyAllWindows