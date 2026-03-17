import time


import paho.mqtt.client as mqtt
import respond

import json
import ota


serial_number = "abc"
# 1. Khởi tạo Client

# 2. Kết nối tới Broker (thay địa chỉ IP và Port tương ứng)
broker_address = "broker.chtlab.us"

my_key = bytes([
    0x35, 0x70, 0x7A, 0x63, 0x74, 0x68, 0x61, 0x50,
    0x54, 0x34, 0x6C, 0x4C, 0x36, 0x4C, 0x49, 0x66,
    0x38, 0x59, 0x47, 0x32, 0x47, 0x30, 0x79, 0x50,
    0x45, 0x47, 0x77, 0x67, 0x36, 0x70, 0x5A, 0x78
])
# 3. Tạo dữ liệu dạng Dictionary (Python)
data_to_send = {
    "serial_number": serial_number,
    "command_type": 101,
    "data": {
        "gun1": {
            "action": 1,
            "order_time": 0,
            "limit_time": 0
        },
        "gun2": {
            "action": 1,
            "order_time": 0,
            "limit_time": 0
        },
        "gun3": {
            "action": 1,
            "order_time": 0,
            "limit_time": 0
        },
        "gun4": {
            "action": 1,
            "order_time": 0,
            "limit_time": 0
        },
        "gun5": {
            "action": 1,
            "order_time": 0,
            "limit_time": 0
        },
        "gun6": {
            "action": 1,
            "order_time": 0,
            "limit_time": 0
        }
    }
}
my_payload ={
  "serial_number": "EV4f00754c3c",
  "command_type": 205,
  "data": {
    "iv": "5515c627c2b6d1723bb8b45f",
    "data": "b4b7b566a8972c6d9fe5db0d43d937a37a7cc8363b8870534c3790ce60e18f547c5c996898d6bb407997587a5e94ea9a6d4616d28ccab89065507c31b63965edace6e46439d10a30893a5af55181abf414a6ed67348126be3040bd21b777ed685d0a9b1c4ba992fa01f67a52fd4ed849db649120fbc964ba8bad91af2818f702dc255a601828468d14f533d7ba1fbb769e058999679f74fdb1865774986ec8b9e8466faaeda54ad6b093dc1289386338abc70e6538fea8ce57dd5fff06acef126fc3369a86e70da2cbaeec817516ea162885e2c3ad",
    "tag": "855d61e5387e88424c6854c910519014"
  }
}
data_pong = {
    "data": {
        "iv": "0315778c736a47d661b3f1e9",
        "data": "83c82d55de6844b72f5dfdce8c7652ad65a54a",
        "tag": "4769e6a3e5223195639fd2a4df101639"
    }
}

def on_connect(client, userdata, flags, rc):
    if rc == 0:
        print("✅ Kết nối thành công!")
        # Đăng ký nhận dữ liệu từ chủ đề (topic) này
        sub_topic = "TEVsafe_"+serial_number
        client.subscribe(sub_topic)
        client.subscribe("PUP4G/SmartEVsafe")
        # client.subscribe("CAMAI/Detectfire")
        # client.subscribe("EVsafe_EV4f00a2bf68")
        # client.subscribe("UP4G/SmartEVsafe")
        # client.subscribe("TUP4G/SmartEVsafe")
        # ota.send_message_ota(ota.link_ota)
    else:
        print(f"❌ Kết nối thất bại, mã lỗi: {rc}")
def on_message(client, userdata, msg):
    try:
        payload = msg.payload.decode()
        data_json = json.loads(payload)
        data_decrypt=respond.giai_ma_chuan(data_json,my_key)
        print("Data decryptred: ", data_decrypt)
    #    print("data: ",data_json)
        ser = data_json["serial_number"]
        print(ser)
        if ser == "broadcast":
            data_send = json.dumps(data_pong)
            client.publish("TUP4G/SmartEVsafe",data_send)
        if ser == "EV013b9cc4ac":

            print("Data decryptred: ", data_decrypt)
        else:
            cmd = int(data_json["command_type"])
            #print("cmd: ",cmd)
            if cmd==101:
                time.sleep(1)
                # print("publish")
                data_send = json.dumps(my_payload)
                client.publish("TUP4G/SmartEVsafe",data_send)

    except Exception as e:
        print("--")
       # print(f"lỗi xử lý dữ liệu {e}")

client = mqtt.Client()
client.on_connect = on_connect
client.on_message = on_message
client.connect(broker_address, 1883)
json_payload = json.dumps(data_to_send)
# 5. Publish lên một Topic
# topic = "TUP4G/SmartEVsafe"
# client.publish(topic, json_payload)
# print(f"Đã gửi JSON: {json_payload}")
client.loop_forever()

# 4. Chuyển Dictionary thành chuỗi JSON
