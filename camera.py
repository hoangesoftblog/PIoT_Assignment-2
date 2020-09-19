import cv2
import facial_recognition
import google_cloud_storage

class VideoCamera:
    def __init__(self):
        self.video = cv2.VideoCapture(0)
        self.gcs = google_cloud_storage.GoogleCloudStorage()

    def __del__(self):
        self.video.release()

    def get_frame_in_bytes(self):
        ret, frame = self.video.read()
        ret2, jpeg = cv2.imencode('.jpg', frame)
        return jpeg.tobytes()