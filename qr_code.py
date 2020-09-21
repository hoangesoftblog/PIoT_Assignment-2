import cv2
import qrcode

def start_reading_qr():
    """Using the installed camera to start searching for QR
    """
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
    """Create a qr code and save them as a png
    ...
    :param content: the content of the qr
    :type content: string
    :param file_name: the name the png is going to be saved as
    :type file_name: string
    """
    # output file name
    filename = str(content) + "_qr.png"
    # generate qr code
    img = qrcode.make(content)
    # save img to a file
    img.save(filename)


if __name__ == "__main__":
    generate_qr_code("2")
