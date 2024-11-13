import streamlit as st
import hashlib
from web3 import Web3
import json
import os

# Thiết lập blockchain giả lập (localhost) - kết nối với một nút blockchain
w3 = Web3(Web3.HTTPProvider('http://127.0.0.1:8545'))  # Cập nhật endpoint của bạn

# Đường dẫn lưu trữ tài khoản
ACCOUNTS_FILE = "accounts.json"
CHAT_HISTORY_FILE = "chat_history.json"

# Hàm tạo địa chỉ blockchain
def create_blockchain_account(password):
    key_bytes = hashlib.sha256(password.encode()).digest()
    encrypted_key = w3.eth.account.encrypt(key_bytes, 'mysecurekey')
    return encrypted_key

# Hàm hash mật khẩu
def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

# Lưu tài khoản vào file JSON
def save_account(username, hashed_password, blockchain_account):
    accounts = load_accounts()
    accounts[username] = {
        "password": hashed_password,
        "blockchain_account": blockchain_account
    }
    with open(ACCOUNTS_FILE, 'w') as file:
        json.dump(accounts, file)

# Tải tài khoản từ file JSON
def load_accounts():
    if os.path.exists(ACCOUNTS_FILE):
        with open(ACCOUNTS_FILE, 'r') as file:
            return json.load(file)
    return {}

# Kiểm tra tài khoản đăng nhập
def check_login(username, password):
    accounts = load_accounts()
    hashed_password = hash_password(password)
    return username in accounts and accounts[username]["password"] == hashed_password

# Lưu tin nhắn vào file JSON
def save_chat_message(username, message):
    chat_history = load_chat_history()
    chat_history.append({"username": username, "message": message})
    with open(CHAT_HISTORY_FILE, 'w') as file:
        json.dump(chat_history, file)

# Tải lịch sử tin nhắn từ file JSON
def load_chat_history():
    if os.path.exists(CHAT_HISTORY_FILE):
        with open(CHAT_HISTORY_FILE, 'r') as file:
            return json.load(file)
    return []

# Tạo giao diện đăng ký
def register():
    st.subheader("Đăng ký")
    username = st.text_input("Tên đăng nhập", key="register_username")
    password = st.text_input("Mật khẩu", type="password", key="register_password")
    if st.button("Đăng ký"):
        if username and password:
            hashed_password = hash_password(password)
            account = create_blockchain_account(password)
            save_account(username, hashed_password, account)
            st.success("Tạo tài khoản blockchain thành công!")
            st.session_state["choice"] = "Đăng nhập"  # Chuyển sang tab "Đăng nhập"
        else:
            st.warning("Vui lòng nhập đầy đủ thông tin!")

# Tạo giao diện đăng nhập
def login():
    st.subheader("Đăng nhập")
    username = st.text_input("Tên đăng nhập", key="login_username")
    password = st.text_input("Mật khẩu", type="password", key="login_password")
    if st.button("Đăng nhập"):
        if check_login(username, password):
            st.session_state['username'] = username
            st.success("Đăng nhập thành công!")
        else:
            st.error("Sai tên đăng nhập hoặc mật khẩu!")

# Tạo trang quản lý tài khoản
def account_management():
    st.subheader("Quản lý tài khoản")
    if st.button("Đăng xuất"):
        del st.session_state['username']
        st.success("Bạn đã đăng xuất thành công")

# Tạo giao diện chính cho ứng dụng chat
def chat_room():
    st.subheader("Phòng Chat")
    if 'username' in st.session_state:
        message = st.text_area("Nhập tin nhắn", key="chat_message")
        if st.button("Gửi"):
            if message:
                save_chat_message(st.session_state['username'], message)
                st.write(f"Tin nhắn đã gửi: {message}")
            else:
                st.warning("Vui lòng nhập tin nhắn!")

        # Hiển thị lịch sử tin nhắn
        st.write("Lịch sử trò chuyện:")
        chat_history = load_chat_history()
        for entry in chat_history:
            st.write(f"{entry['username']}: {entry['message']}")
    else:
        st.warning("Vui lòng đăng nhập để tham gia phòng chat!")

# Điều hướng giao diện
st.sidebar.title("WebChat Blockchain")
if "choice" not in st.session_state:
    st.session_state["choice"] = "Đăng nhập"

# Lựa chọn giao diện theo tùy chọn
choice = st.sidebar.selectbox("Chọn chức năng", ["Đăng nhập", "Đăng ký", "Quản lý tài khoản", "Phòng Chat"], index=["Đăng nhập", "Đăng ký", "Quản lý tài khoản", "Phòng Chat"].index(st.session_state["choice"]))

if choice == "Đăng nhập":
    login()
elif choice == "Đăng ký":
    register()
elif choice == "Quản lý tài khoản":
    if 'username' in st.session_state:
        account_management()
    else:
        st.warning("Vui lòng đăng nhập để quản lý tài khoản!")
elif choice == "Phòng Chat":
    chat_room()

# Cập nhật lựa chọn giao diện vào session_state
st.session_state["choice"] = choice
