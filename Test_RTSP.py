import cv2
import subprocess

# Mở webcam laptop
cap = cv2.VideoCapture(0)

width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
fps = 20

# Lệnh ffmpeg để tạo RTSP stream
command = [
    r"D:\ffmpeg-8.0.1-essentials_build\bin\ffmpeg.exe",
    "-y",
    "-f", "rawvideo",
    "-vcodec", "rawvideo",
    "-pix_fmt", "bgr24",
    "-s", f"{width}x{height}",
    "-r", str(fps),
    "-i", "-",
    "-c:v", "libx264",
    "-preset", "ultrafast",
    "-tune", "zerolatency",
    "-f", "rtsp",
    "rtsp://localhost:8554/laptop"
]

process = subprocess.Popen(command, stdin=subprocess.PIPE)

while True:
    ret, frame = cap.read()
    if not ret:
        break

    process.stdin.write(frame.tobytes())

cap.release()
process.stdin.close()
process.wait()