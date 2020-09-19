import cv2


class VideoCamera(object):
    def __init__(self):
        self.video = cv2.VideoCapture(0)
    
    def __del__(self):
        self.video.release()
    
    # def get_frame(self):
    #     success, image = self.video.read()
    #     ret, jpeg = cv2.imencode('.jpg', image)
    #     return jpeg.tobytes()

    def get_frame(self):
        detector = cv2.QRCodeDetector()

        while True:
            success, image = self.video.read()
            data, bbox, success = detector.detectAndDecode(image)

            if bbox is not None:
                for i in range(len(bbox)):
                    cv2.line(image, tuple(bbox[i][0]), tuple(bbox[(i+1) % len(bbox)][0]), color=(255, 0, 0), thickness=2)

                if data:
                    print("[+] QR Code detected, data:", data)
                    cv2.destroyAllWindows()
                    return data

            cv2.imshow("img", image)
            if cv2.waitKey(1) == ord("q"):
                break

            
        self.video.release()
        cv2.destroyAllWindows()

            
        