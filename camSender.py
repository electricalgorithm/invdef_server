import socket
import struct
import config
from utils import throw
import os

_CONFIG = [config.SERVER_ADDR, config.PORT + 100]  # Add +100 to port number.


def _main__arm():
    import numpy as np
    import picamera
    from time import sleep

    # Networking
    connection = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    while True:
        try:
            connection.bind((_CONFIG[0], _CONFIG[1]))
            break
        except OSError as error:
            throw("ERROR", error)
            if error.errno == 98:
                throw("ERROR", "Port is using by another one. Trying new port.")
                _CONFIG[1] += 1

    connection.listen(5)
    throw("START", f"Server is listening on {socket.gethostbyname(socket.gethostname())}:{_CONFIG[1]}")

    while True:
        conn, addr = connection.accept()
        throw("CLIENT", f"Connection established from {addr}")

        camera = picamera.PiCamera()
        camera.resolution = config.RESOLUTION
        camera.framerate = config.FRAMERATE
        sleep(2)
        image = np.empty((camera.resolution[0], camera.resolution[1], 3), dtype=np.uint8)

        while conn:
            camera.capture(image, 'rgb')
            # Changing numpy.ndarray to bytes
            frame_bytes = image.tobytes(order=None)
            # Structuring the serialized frame's length.
            frame_struct = \
                struct.pack("IIQ",
                            camera.resolution[0],
                            camera.resolution[1],
                            len(frame_bytes)
                            ) + frame_bytes

            # Sending frame to the client
            try:
                conn.sendall(frame_struct)
            except OSError as error:
                if error.errno == 32:
                    throw("ERROR", "[NO:32] Client went down. Restart the client.")
                    conn.close()
                    conn = False
                    break
                continue


def _main__other():
    import cv2

    # Networking
    connection = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    while True:
        try:
            connection.bind((_CONFIG[0], _CONFIG[1]))
            break
        except OSError as error:
            throw("ERROR", error)
            if error.errno == 98:
                throw("ERROR", "Port is using by another one. Trying new port.")
                _CONFIG[1] += 1

    connection.listen(5)
    throw("START", f"Server is listening on {socket.gethostbyname(socket.gethostname())}:{_CONFIG[1]}")

    while True:
        conn, addr = connection.accept()
        throw("CLIENT", f"Connection established from {addr}")

        while conn:
            video_capture = cv2.VideoCapture(0)
            # For better FPS, low quality is optional.
            video_capture.set(cv2.CAP_PROP_FRAME_WIDTH, config.RESOLUTION[1])
            video_capture.set(cv2.CAP_PROP_FRAME_HEIGHT, config.RESOLUTION[0])
            throw("INFO", f"Resolution set to ({int(video_capture.get(cv2.CAP_PROP_FRAME_WIDTH))}, "
                          f"{int(video_capture.get(cv2.CAP_PROP_FRAME_HEIGHT))}) by OpenCV")

            while video_capture.isOpened():
                res, frame = video_capture.read()
                if not res:
                    continue

                # Converting BGR to RGB scheme
                frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                # Changing numpy.ndarray to bytes
                frame_bytes = frame_rgb.tobytes(order=None)
                # Structuring the serialized frame's length.
                frame_struct = \
                    struct.pack("IIQ",
                                int(video_capture.get(cv2.CAP_PROP_FRAME_WIDTH)),
                                int(video_capture.get(cv2.CAP_PROP_FRAME_HEIGHT)),
                                len(frame_bytes)
                                ) + frame_bytes

                # Sending frame to the client
                try:
                    conn.sendall(frame_struct)
                except OSError as error:
                    if error.errno == 32:
                        throw("ERROR", "[NO:32] Client went down. Restart the client.")
                        conn.close()
                        conn = False
                        video_capture.release()
                        break
                    continue


if __name__ == "__main__":
    IS_ARM = os.uname()[4].startswith("arm")
    if IS_ARM:
        throw("INFO", "Camera server is starting in ARM processor mode.")
        _main__arm()
    else:
        throw("INFO", "Camera server is starting in other processor mode.")
        _main__other()
