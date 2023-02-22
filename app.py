import cv2
from flask import Flask, render_template
import threading

cap = cv2.VideoCapture(0)
app = Flask(__name__)

class VideoStream:
    def __init__(self, src=0):
        # Create a VideoCapture object
        self.cap = cv2.VideoCapture(src)

        self.thread = threading.Thread()


@app.route('/')
def home():
    return render_template('index.html')

# while True:
#     success, frame = cap.read()
#     if success:
#         cv2.imshow('frame', frame)
#
#     if cv2.waitKey(1) & 0xFF == ord('q'):
#         break
#
# cap.release()
# cv2.destroyAllWindows()


def main():
    print(type(cap))
    app.run(debug=True)


if __name__ == "__main__":
    main()
