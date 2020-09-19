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
    # initialize the camera
        cap = cv2.VideoCapture(0)
    # initialize the cv2 QRCode detector
        detector = cv2.QRCodeDetector()
        while True:
            _, img = cap.read()
            # detect and decode
            data, bbox, _ = detector.detectAndDecode(img)
            # check if there is a QRCode in the image
            if bbox is not None:
                # display the image with lines
                for i in range(len(bbox)):
                    # draw all lines
                    cv2.line(img, tuple(bbox[i][0]), tuple(bbox[(i+1) % len(bbox)][0]), color=(255, 0, 0), thickness=2)
                if data:
                    print("[+] QR Code detected, data:", data)
                    cap.release()
                    cv2.destroyAllWindows()
                    return data
            # display the result
            cv2.imshow("img", img)
            if cv2.waitKey(1) == ord("q"):
                break
        cap.release()
        cv2.destroyAllWindows()