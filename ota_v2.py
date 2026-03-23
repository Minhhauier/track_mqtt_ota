import time


import paho.mqtt.client as mqtt
import respond

import json
import ota

Current_env = "TEST" #  PROD or DEV or TEST - môi trường thiết bị hiện tại
Updated_env = "PROD" # PROD or DEV or TEST - môi trường sau khi OTA
Serial_number = "abc" # serial_number của thiết bị
broker_address = "broker.chtlab.us"
link_file_bin = "http://ota1.chtlab.us/dev/Essen_4g_prod/Essen_4g_prod_v1_0_3.bin"
my_key = bytes([
    0x35, 0x70, 0x7A, 0x63, 0x74, 0x68, 0x61, 0x50,
    0x54, 0x34, 0x6C, 0x4C, 0x36, 0x4C, 0x49, 0x66,
    0x38, 0x59, 0x47, 0x32, 0x47, 0x30, 0x79, 0x50,
    0x45, 0x47, 0x77, 0x67, 0x36, 0x70, 0x5A, 0x78
])



def on_connect(client, userdata, flags, rc):
    cur_topic = "PUP4G/SmartEVsafe"
    upd_topic = "PUP4G/SmartEVsafe"
    ota_topic = "abc"
    if Current_env == "PROD":
        cur_topic = "PUP4G/SmartEVsafe"
        ota_topic = "PEVsafe_"+Serial_number
    elif Current_env == "DEV":
        cur_topic = "UP4G/SmartEVsafe"
        ota_topic = "EVsafe_"+Serial_number
    elif Current_env == "TEST":
        cur_topic = "TUP4G/SmartEVsafe"
        ota_topic = "TEVsafe_"+Serial_number
    if Updated_env == "PROD":
        upd_topic = "PUP4G/SmartEVsafe"
    elif Updated_env == "DEV":
        upd_topic = "UP4G/SmartEVsafe"
    elif Updated_env == "TEST":
        upd_topic = "TUP4G/SmartEVsafe"
    if rc == 0:
        print("✅ Kết nối thành công!")
        client.subscribe(cur_topic)
        client.subscribe(upd_topic)
        ota.send_message_ota(Serial_number, ota_topic, link_file_bin)
    else:
        print(f"❌ Kết nối thất bại, mã lỗi: {rc}")
def on_message(client, userdata, msg):
    try:
        payload = msg.payload.decode()
        data_json = json.loads(payload)
        data_decrypt=respond.giai_ma_chuan(data_json,my_key)
        ser = data_json["serial_number"]
        # print(ser)
        if ser == Serial_number:
            print("Data decryptred: ", data_decrypt)

    except Exception as e:
        print("--")
       # print(f"lỗi xử lý dữ liệu {e}")

client = mqtt.Client()
client.on_connect = on_connect
client.on_message = on_message
client.connect(broker_address, 1883)
# 5. Publish lên một Topic
# topic = "TUP4G/SmartEVsafe"
# client.publish(topic, json_payload)
# print(f"Đã gửi JSON: {json_payload}")
client.loop_forever()

# 4. Chuyển Dictionary thành chuỗi JSON
