from sympy import true
from ultralytics import YOLO
import cv2

model = YOLO("best.pt")

cap = cv2.VideoCapture(0)

while True:
    ret, frame = cap.read() #ret is true if read successfully-frame anh lay tu webcam
    if not ret:
        break
    result = model(frame)#đưa frame vao model
    annotated_frame = result[0].plot() # kết qủa của frame đầu tiên, trong trường hợp này chỉ có một frame vì mỗi lần chỉ đưa vào 1 frame ... .plot ve Bounding box, ten class, confidence
    cv2.imshow("YOLO Webcam", annotated_frame)

    if cv2.waitKey(1) & 0xFF == ord('q'): ## cho 1ms neu nguoi dung bam q thi thoat vong lap
        break

cap.release() #tat cam
cv2.destroyAllWindows() #Dong all cua so opencv


