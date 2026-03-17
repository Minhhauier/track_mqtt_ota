import os
import binascii
import json
import hashlib
from cryptography.hazmat.primitives.ciphers.aead import AESGCM


# --- 1. HÀM TẠO KEY TỪ PASSWORD ---
def get_key_from_password(password):
    # AES-256 yêu cầu key 32 bytes.
    # Ta dùng hàm băm SHA-256 để biến "1234" thành chuỗi 32 bytes cố định.
    return hashlib.sha256(password.encode('utf-8')).digest()


# --- 2. HÀM MÃ HÓA (Encrypt) ---
def ma_hoa(plaintext, password):
    # Tạo key chuẩn
    key = get_key_from_password(password)

    # Tạo IV ngẫu nhiên (12 bytes là chuẩn cho GCM)
    iv = os.urandom(16)

    # Khởi tạo AES-GCM
    aesgcm = AESGCM(key)

    # Mã hóa (Thư viện trả về Ciphertext nối liền với Tag)
    # data_encrypted = Ciphertext + Tag (16 bytes cuối)
    data_encrypted = aesgcm.encrypt(iv, plaintext.encode('utf-8'), None)

    # Tách Tag và Ciphertext riêng ra để giống định dạng JSON của bạn
    tag = data_encrypted[-16:]  # 16 bytes cuối là Tag
    ciphertext = data_encrypted[:-16]  # Phần còn lại là dữ liệu

    # Đóng gói vào JSON và chuyển sang Hex
    result = {
        "iv": binascii.hexlify(iv).decode('utf-8'),
        "data": binascii.hexlify(ciphertext).decode('utf-8'),
        "tag": binascii.hexlify(tag).decode('utf-8')
    }
    return result


# --- 3. HÀM GIẢI MÃ (Decrypt) ---
def giai_ma(json_obj, password):
    try:
        # Tạo lại key y hệt lúc mã hóa
        key = get_key_from_password(password)

        # Chuyển Hex string về dạng Bytes
        iv = binascii.unhexlify(json_obj["iv"])
        ciphertext = binascii.unhexlify(json_obj["data"])
        tag = binascii.unhexlify(json_obj["tag"])

        # Ghép lại Ciphertext + Tag (vì hàm decrypt yêu cầu gộp chung)
        full_data = ciphertext + tag

        # Khởi tạo AES-GCM
        aesgcm = AESGCM(key)

        # Giải mã
        decrypted_data = aesgcm.decrypt(iv, full_data, None)
        return decrypted_data.decode('utf-8')

    except Exception as e:
        return f"Lỗi giải mã: {str(e)} (Sai Key hoặc dữ liệu bị sửa đổi)"



# --- 4. CHẠY THỬ NGHIỆM ---

# Mật khẩu giả định
my_password = bytes([
    0x35, 0x70, 0x7A, 0x63, 0x74, 0x68, 0x61, 0x50,
    0x54, 0x34, 0x6C, 0x4C, 0x36, 0x4C, 0x49, 0x66,
    0x38, 0x59, 0x47, 0x32, 0x47, 0x30, 0x79, 0x50,
    0x45, 0x47, 0x77, 0x67, 0x36, 0x70, 0x5A, 0x78
])
original_text = "Xin chào, đây là dữ liệu mật!"

print(f"--- BẮT ĐẦU VỚI PASSWORD: {my_password} ---\n")

du_lieu_mau = {
  "serial_number": "EV4f0075481c",
  "command_type": 205,
  "data": {
    "iv": "5515c627c2b6d1723bb8b45f",
    "data": "b4b7b566a8972c6d9fe5db0d43d937a37a7cc8363b8870534c3790ce60e18f547c5c996898d6bb407997587a5e94ea9a6d4616d28ccab89065507c31b63965edace6e46439d10a30893a5af55181abf414a6ed67348126be3040bd21b777ed685d0a9b1c4ba992fa01f67a52fd4ed849db649120fbc964ba8bad91af2818f702dc255a601828468d14f533d7ba1fbb769e058999679f74fdb1865774986ec8b9e8466faaeda54ad6b093dc1289386338abc70e6538fea8ce57dd5fff06acef126fc3369a86e70da2cbaeec817516ea162885e2c3ad",
    "tag": "855d61e5387e88424c6854c910519014"
  }
}


# C. Thử giải mã với mật khẩu sai
def giai_ma_chuan(input_json, raw_key):
    try:
        # Lấy dữ liệu từ cấu trúc lồng nhau
        crypto_data = input_json.get("data", {})

        iv_hex = crypto_data["iv"]
        cipher_hex = crypto_data["data"]
        tag_hex = crypto_data["tag"]

        # Convert Hex -> Bytes
        iv = binascii.unhexlify(iv_hex)
        ciphertext = binascii.unhexlify(cipher_hex)
        tag = binascii.unhexlify(tag_hex)

        # Tạo đối tượng AES-GCM với raw key
        aesgcm = AESGCM(raw_key)

        # Giải mã (Ciphertext + Tag)
        plaintext = aesgcm.decrypt(iv, ciphertext + tag, None)

        return plaintext.decode('utf-8')

    except Exception as e:
        return f"Lỗi: {e}"


def tao_goi_tin_ma_hoa(payload_dict, serial_number, cmd_type, key):
    # BƯỚC 1: Chuyển dữ liệu JSON (Dict) thành Chuỗi (String) rồi sang Bytes
    # separators=(',', ':') giúp xóa khoảng trắng thừa để tiết kiệm dung lượng (chuẩn IoT)
    payload_str = json.dumps(payload_dict, separators=(',', ':'))
    payload_bytes = payload_str.encode('utf-8')

    # BƯỚC 2: Tạo IV ngẫu nhiên (12 bytes)
    iv = os.urandom(16)

    # BƯỚC 3: Mã hóa AES-GCM
    aesgcm = AESGCM(key)
    # Kết quả trả về là: Ciphertext + Tag (16 bytes cuối)
    encrypted_blob = aesgcm.encrypt(iv, payload_bytes, None)

    # BƯỚC 4: Tách Tag và Ciphertext
    tag = encrypted_blob[-16:]  # Lấy 16 byte cuối làm Tag
    ciphertext = encrypted_blob[:-16]  # Phần còn lại là dữ liệu đã mã hóa

    # BƯỚC 5: Đóng gói thành cấu trúc JSON đích
    packet = {
        "serial_number": serial_number,
        "command_type": cmd_type,
        "data": {
            "iv": binascii.hexlify(iv).decode('utf-8'),
            "data": binascii.hexlify(ciphertext).decode('utf-8'),
            "tag": binascii.hexlify(tag).decode('utf-8')
        }
    }

    return packet




# --- CHẠY ---
print(f"Key (Hex): {binascii.hexlify(my_password).decode()}")
print("-" * 40)
ket_qua = giai_ma_chuan(du_lieu_mau, my_password)
print("NỘI DUNG GIẢI MÃ ĐƯỢC:")
print(ket_qua)
print("-" * 40)
# --- DỮ LIỆU ĐẦU VÀO CỦA BẠN ---
my_payload = "pong_"+"EV4f00754c3c"
my_serial = "broadcast"
my_cmd = "ping"

# --- THỰC HIỆN ---
ket_qua = tao_goi_tin_ma_hoa(my_payload, my_serial, my_cmd, my_password)

# --- IN KẾT QUẢ ---
print("JSON ĐÃ MÃ HÓA (Để gửi đi):")
print(json.dumps(ket_qua, indent=2))