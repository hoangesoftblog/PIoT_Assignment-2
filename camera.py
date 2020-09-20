import cv2
import facial_recognition
import google_cloud_storage
import os

class VideoCamera:
    def __init__(self):
        self.video = cv2.VideoCapture(0)
        self.gcs = google_cloud_storage.GoogleCloudStorage()
        self.face_detector = cv2.CascadeClassifier('haarcascade_frontalface_default.xml')
        # Random variable used
        self.count = 0

    def __del__(self):
        self.video.release()


    def get_frame_in_bytes(self):
        ret, frame = self.video.read()
        ret2, jpeg = cv2.imencode('.jpg', frame)
        return jpeg.tobytes()

    def read():
        return self.video.read()


    def capture_faces(self, UID):
        """
        When run will start capturing images of faces on the camera, and save it on the cloud
        Naming scheme is based on id
        :param UID: User ID to capture face
        :type UID: str or int
        :return: void
        """
        
        # Capture camera frame
        _, frame = self.video.read()

        # Convert to grayscale and Histogram Equalization it
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        gray = cv2.equalizeHist(gray)

        if self.count < 20:
            # Then trying to detect all the faces in the pictures
            faces = self.face_detector.detectMultiScale(gray, 1.3, 5)
            for (x, y, w, h) in faces:
                # Draw borders for all the faces found
                cv2.rectangle(frame, (x,y), (x+w, y+h), (255,0 ,0) , 2)
                self.count += 1

                # Show how many pictures captured
                cv2.rectangle(frame, (x - 22, y - 90), (x + w + 22, y - 22), (0, 255, 0), -1)
                cv2.putText(frame, str(self.count), (x, y - 40), cv2.FONT_HERSHEY_SIMPLEX, 2, (255, 255, 255), 3)

                # Since the image is still in Stream, we have to export it into files 
                # and then upload it
                # Then delete it to save spaces
                file_name = "User " + str(UID) + ' - ' + str(self.count) + ".jpg"
                cv2.imwrite(file_name, gray[y:y+h, x:x+w])
                self.gcs.upload_from_filename(file_name, file_name)
                # if os.path.exists(file_name):
                #     os.remove(file_name)
        else:
            pass

        ret2, jpeg = cv2.imencode('.jpg', frame)
        return jpeg.tobytes()
            

if __name__ == "__main__":
    pass