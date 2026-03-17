from ultralytics import YOLO

model = YOLO("best_float16.tflite")
results = model("fire.64.png")
results[0].show()