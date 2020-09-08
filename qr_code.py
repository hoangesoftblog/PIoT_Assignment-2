import cv2
import qrcode

def start_reading_qr():
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

def generate_qr_code(content,file_name):
    # output file name
    filename = str(file_name) + "_qr.png"
    # generate qr code
    img = qrcode.make(content)
    # save img to a file
    img.save(filename)
