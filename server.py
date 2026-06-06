import paho.mqtt.client as mqtt
import firebase_admin
from firebase_admin import credentials
from firebase_admin import db
import json
import time

# ==========================================
# 1. KHỞI TẠO FIREBASE ADMIN
# ==========================================
# Trỏ đường dẫn tới file khóa bí mật của bạn
cred = credentials.Certificate('serviceAccountKey.json')

# Nhập URL Realtime Database của bạn
firebase_admin.initialize_app(cred, {
    'databaseURL': 'https://gpstracker-group1-default-rtdb.firebaseio.com'
})

# ==========================================
# 2. CẤU HÌNH MQTT BROKER
# ==========================================
MQTT_BROKER = "44d783950c204afea2e2ca6664ce133e.s1.eu.hivemq.cloud"  # Thay bằng IP/Domain Broker của bạn
MQTT_PORT = 8883  # Cổng mặc định của MQTT
MQTT_TOPIC_PUB = "SmartHome/PUB"
MQTT_TOPIC_SUB = "SmartHome/SUB"


# Hàm chạy khi kết nối thành công với Broker
def on_connect(client, userdata, flags, rc):
    if rc == 0:
        print("✅ Đã kết nối thành công tới MQTT Broker!")
        client.subscribe(MQTT_TOPIC_PUB)
        client.subscribe(MQTT_TOPIC_SUB)
        print(f" Đang lắng nghe dữ liệu từ topic: {MQTT_TOPIC_SUB} và {MQTT_TOPIC_PUB}")
    else:
        print(f"❌ Kết nối thất bại, mã lỗi: {rc}")


# Hàm chạy khi có tin nhắn mới từ ESP32
def on_message(client, userdata, msg):
    payload = msg.payload.decode('utf-8')
    print(f"\n📨 Nhận dữ liệu từ [{msg.topic}]: {payload}")

    try:
        # Giả sử dữ liệu ESP32 gửi là JSON (vd: {"nhiet_do": 25, "do_am": 60})
        data = json.loads(payload)

        # Thêm timestamp hiện tại (millisecond) vào dữ liệu
        data['thoi_gian'] = int(time.time() * 1000)

        # Trỏ tới node 'thong_tin_thiet_bi' và push dữ liệu lên
        ref = db.reference('thong_tin_thiet_bi')
        ref.push(data)

        print("☁️ Đã cập nhật thành công lên Firebase Realtime Database!")

    except json.JSONDecodeError:
        print("⚠️ Lỗi: Dữ liệu nhận được không phải chuỗi JSON hợp lệ.")
    except Exception as e:
        print(f"❌ Lỗi khi đẩy lên Firebase: {e}")


# ==========================================
# 3. CHẠY MQTT CLIENT
# ==========================================
client = mqtt.Client()
client.on_connect = on_connect
client.on_message = on_message

# Nếu Broker có user/password, hãy bỏ comment dòng dưới và điền vào:
# client.username_pw_set("my_user", "my_password")

print("Đang kết nối tới Broker...")
client.connect(MQTT_BROKER, MQTT_PORT, 60)

# Chạy vòng lặp vô hạn để duy trì kết nối và chờ tin nhắn
try:
    client.loop_forever()
except KeyboardInterrupt:
    print("\nĐã dừng chương trình.")