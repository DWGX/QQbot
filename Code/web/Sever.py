# server.py

import ipaddress
import os
import sys
import asyncio
import base64
import json
import uuid
from datetime import datetime

import websockets
from websockets.exceptions import ConnectionClosedOK, ConnectionClosedError
from PySide6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QTextEdit, QLineEdit,
    QPushButton, QLabel, QListWidget, QMessageBox, QHBoxLayout
)
from PySide6.QtCore import Qt
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives import padding
from cryptography.hazmat.backends import default_backend
from qasync import QEventLoop

class ChatServer:
    def __init__(self, gui, host='0.0.0.0', port=6666):
        self.host = host
        self.port = port
        self.gui = gui
        self.clients = {}  # {ip: {"websocket": websocket, "session_key": session_key_bytes}}
        self.blocked_ips = set()
        self.server = None

        # 预共享密钥，需与客户端保持一致（32字节对应256位AES密钥）
        self.PRE_SHARED_KEY = b'G6JrXcZLw1Q8P3F7d9K0M2N4B6V8Y1A3'  # 替换为您的32字节密钥

        # 验证预共享密钥长度
        if len(self.PRE_SHARED_KEY) != 32:
            raise ValueError("预共享密钥长度不正确。应为32字节。")
        else:
            print("预共享密钥长度验证通过。")

    async def handle_client(self, websocket, path):
        user_id = str(uuid.uuid4())
        ip = websocket.remote_address[0]

        # 获取 X-Forwarded-For 请求头中的 IP
        forwarded_for = websocket.request_headers.get('X-Forwarded-For')
        if forwarded_for:
            ip = forwarded_for.split(',')[0].strip()

        if not self.is_valid_ip(ip):
            print(f"无效的IP地址: {ip}")
            await websocket.close()
            return

        if ip in self.blocked_ips:
            await websocket.close()
            self.gui.display_message(f"{datetime.now().strftime('%H:%M:%S')} 系统: 拒绝来自 {ip} 的连接（已被拉黑）")
            return

        # 等待客户端发送真实 IP 地址
        try:
            client_ip_message = await asyncio.wait_for(websocket.recv(), timeout=30)
            client_ip_data = json.loads(client_ip_message)
            if client_ip_data.get("type") == "client_ip":
                ip = client_ip_data.get("ip", ip)
        except asyncio.TimeoutError:
            print(f"客户端 {ip} 发送IP地址超时")
            await websocket.close()
            return
        except json.JSONDecodeError:
            print(f"客户端 {ip} 发送了无效的JSON数据")
            await websocket.close()
            return

        if not self.is_valid_ip(ip):
            print(f"无效的IP地址: {ip}")
            await websocket.close()
            return

        if ip in self.blocked_ips:
            await websocket.close()
            self.gui.display_message(f"{datetime.now().strftime('%H:%M:%S')} 系统: 拒绝来自 {ip} 的连接（已被拉黑）")
            return

        # 将客户端信息存储
        self.clients[ip] = {"websocket": websocket, "session_key": None}
        self.gui.add_client(f"{ip}")
        print(f"客户端 {ip} 已连接")

        try:
            # 接收密钥交换请求
            key_exchange_request = await asyncio.wait_for(websocket.recv(), timeout=30)
            key_exchange_data = json.loads(key_exchange_request)
            if key_exchange_data.get('type') != 'request_session_key':
                print(f"未识别的密钥交换请求类型: {key_exchange_data.get('type')}")
                await websocket.close()
                return

            # 生成会话密钥
            session_key_bytes = os.urandom(32)  # 32字节 = 256位
            session_key_b64 = base64.b64encode(session_key_bytes).decode('utf-8')

            # 加密会话密钥
            encrypted_session_key = self.encrypt_message(session_key_b64, self.PRE_SHARED_KEY)

            # 发送会话密钥给客户端
            session_key_message = {
                'type': 'session_key',
                'session_key': encrypted_session_key
            }
            await websocket.send(json.dumps(session_key_message))
            print(f"已发送加密的会话密钥给 {ip}")

            # 存储会话密钥（作为字节）
            self.clients[ip]["session_key"] = session_key_bytes
            print(f"存储的会话密钥为: {self.clients[ip]['session_key']} (type: {type(self.clients[ip]['session_key'])})")

            # 广播系统消息
            await self.broadcast_system_message(
                f"{datetime.now().strftime('%H:%M:%S')} 系统: 欢迎 {ip} 加入聊天")

            # 更新在线用户列表
            await self.update_online_users()

            async for encrypted_message in websocket:
                decrypted_message = self.decrypt_message(encrypted_message, self.clients[ip]["session_key"])
                if not decrypted_message:
                    continue

                await self.handle_message(ip, decrypted_message)

        except (asyncio.TimeoutError, ConnectionClosedOK, ConnectionClosedError):
            print(f"连接超时或断开：{ip}")
        except Exception as e:
            print(f"处理客户端 {ip} 时出错: {e}")
        finally:
            self.remove_client(ip)
            await self.update_online_users()  # 移除用户后更新在线用户列表

    async def update_online_users(self):
        users_list = []
        for ip, client_info in self.clients.items():
            users_list.append(
                {"ip": ip}
            )
        await self.broadcast({
            "type": "update_online_users",
            "users": users_list
        })

    def is_valid_ip(self, ip):
        try:
            ipaddress.ip_address(ip)
            return True
        except ValueError:
            return False

    def encrypt_message(self, message, key):
        # AES-CBC加密
        # message: str (UTF-8)
        # key: bytes (32 bytes)
        if isinstance(message, str):
            message = message.encode('utf-8')
        if isinstance(key, str):
            key = key.encode('utf-8')
        iv = os.urandom(16)  # 128-bit IV
        cipher = Cipher(algorithms.AES(key), modes.CBC(iv), backend=default_backend())
        encryptor = cipher.encryptor()
        padder = padding.PKCS7(128).padder()
        padded_data = padder.update(message) + padder.finalize()
        ciphertext = encryptor.update(padded_data) + encryptor.finalize()
        # 将IV和密文拼接并进行Base64编码
        iv_ciphertext = iv + ciphertext
        return base64.b64encode(iv_ciphertext).decode('utf-8')

    def decrypt_message(self, encrypted_message, key):
        try:
            # encrypted_message: base64 string
            # key: bytes (32 bytes)
            iv_ciphertext = base64.b64decode(encrypted_message)
            iv = iv_ciphertext[:16]
            ciphertext = iv_ciphertext[16:]
            cipher = Cipher(algorithms.AES(key), modes.CBC(iv), backend=default_backend())
            decryptor = cipher.decryptor()
            padded_plaintext = decryptor.update(ciphertext) + decryptor.finalize()
            unpadder = padding.PKCS7(128).unpadder()
            plaintext = unpadder.update(padded_plaintext) + unpadder.finalize()
            return plaintext.decode('utf-8')
        except Exception as e:
            print(f"Error decrypting message: {e}")
            return None

    async def handle_message(self, ip, message):
        try:
            message_data = json.loads(message)
        except json.JSONDecodeError:
            print(f"消息解析失败: {message}")
            return

        msg_type = message_data.get('type')

        if msg_type == 'message':
            timestamp = datetime.now().strftime('%H:%M:%S')
            broadcast_data = {
                'type': 'message',
                'id': message_data.get('id'),
                'timestamp': timestamp,
                'username': ip,  # 使用IP作为用户名
                'content': message_data.get('content')
            }
            await self.broadcast(broadcast_data)
            self.gui.display_message(f"{timestamp} {ip}: {message_data.get('content')}")
        elif msg_type == 'image':
            timestamp = datetime.now().strftime('%H:%M:%S')
            broadcast_data = {
                'type': 'image',
                'id': message_data.get('id'),
                'timestamp': timestamp,
                'username': ip,
                'content': message_data.get('content')  # Base64字符串
            }
            await self.broadcast(broadcast_data)
            self.gui.display_message(f"{timestamp} {ip} 发送了一张图片。")
        elif msg_type == 'edit_image':
            # 处理编辑后的图片
            edit_broadcast_data = {
                'type': 'edit_image',
                'id': message_data.get('id'),
                'newContent': message_data.get('newContent')
            }
            await self.broadcast(edit_broadcast_data)
            self.gui.display_message(f"{datetime.now().strftime('%H:%M:%S')} 系统: {ip} 修改了一张图片。")
        elif msg_type == 'revoke':
            await self.broadcast(message_data)
            self.gui.display_message(f"{datetime.now().strftime('%H:%M:%S')} 系统: {ip} 撤回了一条消息")
        elif msg_type == 'edit':
            # 处理编辑消息
            edit_broadcast_data = {
                'type': 'edit',
                'id': message_data.get('id'),
                'newContent': message_data.get('newContent')
            }
            await self.broadcast(edit_broadcast_data)
            self.gui.display_message(f"{datetime.now().strftime('%H:%M:%S')} 系统: {ip} 修改了一条消息")
        else:
            print(f"未知的消息类型: {msg_type}")

    def remove_client(self, ip):
        client_info = self.clients.pop(ip, None)
        if client_info:
            websocket = client_info["websocket"]
            self.gui.remove_client(ip)
            print(f"客户端 {ip} 已断开")

    async def broadcast(self, data):
        message = json.dumps(data)
        for ip, client_info in self.clients.items():
            websocket = client_info["websocket"]
            session_key = client_info["session_key"]  # bytes
            if not session_key:
                continue
            encrypted_message = self.encrypt_message(message, session_key)
            try:
                await websocket.send(encrypted_message)
            except Exception as e:
                print(f"Error sending message to client {ip}: {e}")

    async def broadcast_system_message(self, message):
        broadcast_data = {
            'type': 'system',
            'timestamp': datetime.now().strftime('%H:%M:%S'),
            'content': message
        }
        await self.broadcast(broadcast_data)
        self.gui.display_message(message)

    async def start_server(self):
        self.server = await websockets.serve(self.handle_client, self.host, self.port)
        self.gui.update_status(f"服务器运行中: {self.host}:{self.port} (WS)")
        print(f"服务器运行中: {self.host}:{self.port} (WS)")
        await self.server.wait_closed()

    def stop_server(self):
        if self.server:
            self.server.close()
            self.gui.display_message(f"{datetime.now().strftime('%H:%M:%S')} 系统: 服务器已关闭")
            print(f"{datetime.now().strftime('%H:%M:%S')} 系统: 服务器已关闭")

class ServerGUI(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Websocket 内网穿透 TCP 中转")
        self.setGeometry(100, 100, 800, 600)
        self.setup_ui()
        self.server = None

    def setup_ui(self):
        self.layout = QVBoxLayout(self)

        self.status_label = QLabel("服务器未启动")
        self.layout.addWidget(self.status_label)

        self.port_input = QLineEdit()
        self.port_input.setPlaceholderText("输入自定义端口号（默认：6666）")
        self.layout.addWidget(self.port_input)

        self.chat_display = QTextEdit()
        self.chat_display.setReadOnly(True)
        self.layout.addWidget(self.chat_display)

        self.client_list = QListWidget()
        self.layout.addWidget(QLabel("当前连接的客户端 IP"))
        self.layout.addWidget(self.client_list)

        self.setup_controls()

    def setup_controls(self):
        message_layout = QHBoxLayout()
        self.message_input = QLineEdit()
        self.message_input.setPlaceholderText("输入服务器消息")
        message_layout.addWidget(self.message_input)
        send_button = QPushButton("发送")
        send_button.clicked.connect(self.send_message)
        send_button.setStyleSheet("margin-left: 10px;")
        message_layout.addWidget(send_button)
        self.layout.addLayout(message_layout)

        block_layout = QHBoxLayout()
        self.block_input = QLineEdit()
        self.block_input.setPlaceholderText("输入要拉黑/解除拉黑的IP")
        block_layout.addWidget(self.block_input)
        block_button = QPushButton("拉黑IP")
        block_button.clicked.connect(self.block_ip)
        block_layout.addWidget(block_button)
        unblock_button = QPushButton("解除拉黑IP")
        unblock_button.clicked.connect(self.unblock_ip)
        block_layout.addWidget(unblock_button)
        self.layout.addLayout(block_layout)

        start_button = QPushButton("启动服务器")
        start_button.clicked.connect(self.start_server)
        self.layout.addWidget(start_button)

        shutdown_button = QPushButton("关闭服务器")
        shutdown_button.clicked.connect(self.shutdown_server)
        self.layout.addWidget(shutdown_button)

        self.client_list.itemDoubleClicked.connect(self.on_client_double_clicked)


    def on_client_double_clicked(self, item):
        self.block_input.setText(item.text())

    def display_message(self, message):
        self.chat_display.append(message)

    def add_client(self, client_ip):
        if not self.client_list.findItems(client_ip, Qt.MatchExactly):
            self.client_list.addItem(client_ip)

    def remove_client(self, client_ip):
        for item in self.client_list.findItems(client_ip, Qt.MatchExactly):
            self.client_list.takeItem(self.client_list.row(item))

    def update_status(self, status):
        self.status_label.setText(status)

    def start_server(self):
        port = self.port_input.text().strip() or "6666"  # 默认端口
        if port.isdigit():
            self.server = ChatServer(self, port=int(port))  # 使用自定义端口
            asyncio.ensure_future(self.server.start_server())  # This is where the server actually starts.
            self.update_status(f"服务器运行中: 0.0.0.0:{port} (WS)")
        else:
            QMessageBox.warning(self, '错误', '请输入有效的端口号。')

    def send_message(self):
        message = self.message_input.text().strip()
        if message:
            asyncio.create_task(self.server.broadcast({
                'type': 'message',
                'id': 'server_' + str(int(datetime.now().timestamp())),
                'timestamp': datetime.now().strftime('%H:%M:%S'),
                'username': '系统',
                'content': message
            }))
            self.display_message(f"{datetime.now().strftime('%H:%M:%S')} 系统: {message}")
            self.message_input.clear()

    def block_ip(self):
        ip = self.block_input.text().strip()
        if ip:
            if self.server.is_valid_ip(ip):
                self.server.blocked_ips.add(ip)
                self.display_message(f"{datetime.now().strftime('%H:%M:%S')} 系统: 已拉黑IP {ip}")
                self.block_input.clear()
            else:
                QMessageBox.warning(self, '错误', '请输入有效的IP地址。')

    def unblock_ip(self):
        ip = self.block_input.text().strip()
        if ip and ip in self.server.blocked_ips:
            self.server.blocked_ips.remove(ip)
            self.display_message(f"{datetime.now().strftime('%H:%M:%S')} 系统: 已解除拉黑IP {ip}")
            self.block_input.clear()
        elif ip:
            QMessageBox.information(self, '信息', f"IP {ip} 未被拉黑。")

    def shutdown_server(self):
        if QMessageBox.question(self, '关闭服务器', '确定要关闭服务器吗?', QMessageBox.Yes | QMessageBox.No) == QMessageBox.Yes:
            self.server.stop_server()
            QApplication.quit()


def main():
    app = QApplication(sys.argv)
    loop = QEventLoop(app)
    asyncio.set_event_loop(loop)
    gui = ServerGUI()
    gui.show()
    # You don't need to call gui.server.start_server() here since it will be called within the GUI when the user starts the server.

    with loop:
        loop.run_forever()


if __name__ == "__main__":
    main()
