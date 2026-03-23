import respond
import json
import paho.mqtt.client as mqtt
broker_address = "broker.chtlab.us"
topic = "abc" # ví dụ topic = "TEVsafe_EV8cfe4390dc"
link_ota = "http://ota1.chtlab.us/dev/Essen_4g_prod/Essen_4g_prod_v_1_1_2.bin" #link file bin muốn lưu
my_password = bytes([
    0x35, 0x70, 0x7A, 0x63, 0x74, 0x68, 0x61, 0x50,
    0x54, 0x34, 0x6C, 0x4C, 0x36, 0x4C, 0x49, 0x66,
    0x38, 0x59, 0x47, 0x32, 0x47, 0x30, 0x79, 0x50,
    0x45, 0x47, 0x77, 0x67, 0x36, 0x70, 0x5A, 0x78
])
def send_message_ota(serial_number,link):

    data_to_send = {
        "data": {
            "ver": "2.0",
            "link1": "http://ota1.chtlab.us/dev/Essen_4g_prod/Essen_4g_prod_v1_0_3.bin",
            "link2": link
        }
    }

    # tạo gói tin mã hóa
    data = respond.tao_goi_tin_ma_hoa(data_to_send, serial_number, 400, my_password)

    payload = json.dumps(data, separators=(',', ':'))

    # tạo MQTT client
    client = mqtt.Client()

    # kết nối broker
    client.connect(broker_address, 1883, 60)

    # publish
    client.publish(topic, payload)

    print(f"Published message to topic {topic} :")
    print(payload)

    client.disconnect()


def main():
    send_message_ota(link_ota)
if __name__ == "__main__":
    main()
