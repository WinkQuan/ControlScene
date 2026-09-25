# coding: utf-8
from socket import *
import settings
import os
import cv2
import base64
import time
import sys
from threading import Thread
from GenerateFromText import generate
import shutil

from tencentcloud.common import credential
from tencentcloud.common.profile.client_profile import ClientProfile
from tencentcloud.common.profile.http_profile import HttpProfile
from tencentcloud.common.exception.tencent_cloud_sdk_exception import TencentCloudSDKException
from tencentcloud.tmt.v20180321 import tmt_client, models
import json


class Server:
    def __init__(self, host=settings.ip_addr, port=settings.port):
        self.socket = socket(AF_INET, SOCK_STREAM)  # 使用IPv4和TCP
        self.host = host
        self.port = port

    def bind(self):
        """绑定并监听端口"""
        self.socket.bind((self.host, self.port))
        self.socket.listen(5)  # 设置最大连接数为5
        print(f"服务端启动完成，监听地址为:{self.host}:{self.port}")

    def close(self):
        """关闭监听套接字"""
        self.socket.close()

    def base64_encode_img(self, img_data):
        """将图像编码为Base64"""
        _, image_encoded = cv2.imencode('.jpg', img_data)
        image_bytes = image_encoded.tobytes()
        image_base64 = base64.b64encode(image_bytes).decode('utf-8')
        return image_base64

    def get_img(self, img_path):
        """读取图像并返回Base64编码的字节数据"""
        img = cv2.imread(img_path)
        img_d = self.base64_encode_img(img)
        img_b = img_d.encode()
        return img_b

    def send_img(self, con, img_path):
        """发送图像数据"""
        img_data = self.get_img(img_path)
        n = 0
        print("图像数据大小:", len(img_data))

        size = len(img_data)
        transtime = (size // 1024) + (1 if size % 1024 else 0)
        print("需要发送的次数:", transtime)
        con.send_msg(str(transtime))
        time.sleep(1)

        while n < len(img_data):
            con.conn.send(img_data[n:n + 1024])
            n += 1024
        print(f"已发送:{img_path}")

#进行翻译操作
def translate(text_information):
    secret_id = os.environ.get("TENCENTCLOUD_SECRET_ID")
    secret_key = os.environ.get("TENCENTCLOUD_SECRET_KEY")
    if not secret_id or not secret_key:
        raise RuntimeError(
            "Set TENCENTCLOUD_SECRET_ID and TENCENTCLOUD_SECRET_KEY "
            "before using translation."
        )

    try:
        cred = credential.Credential(secret_id, secret_key)
        httpProfile = HttpProfile()
        httpProfile.endpoint = "tmt.tencentcloudapi.com"
    
        clientProfile = ClientProfile()
        clientProfile.httpProfile = httpProfile
        client = tmt_client.TmtClient(cred, "ap-beijing", clientProfile)

        req = models.TextTranslateRequest()
        req.SourceText = text_information#要翻译的语句
        req.Source ='zh'#源语言类型
        req.Target ='en'#目标语言类型
        req.ProjectId = 0

        resp = client.TextTranslate(req)
        data=json.loads(resp.to_json_string())
        # print(data['TargetText'])
        text_en_information = data['TargetText']
        return text_en_information


    except TencentCloudSDKException as err:
        print(err)

def text_input(text):
    """根据输入的文本修改配置文件"""
    file_path = '/home/ubuntu/zhouzhi/SceneDreamer360/data/prompt.txt'
    with open(file_path, 'w') as file:
        file.write(text)
        print(f"文件 '{file_path}' 已更新。")

    file_path2 = '/home/ubuntu/zhouzhi/SceneDreamer360/data/Matterport3D/mp3d_skybox/e9zR4mvMWw7/blip3_stitched/test.txt'
    if not os.path.exists(file_path2):
        with open(file_path2, 'w') as file:
            file.write('')  # 创建空文件
            print(f"文件 '{file_path2}' 已创建。")
    else:
        print(f"文件 '{file_path2}' 已存在。")

def delete_folder(folder_path):
    if os.path.exists(folder_path) and os.path.isdir(folder_path):
        shutil.rmtree(folder_path)
        print(f"The folder {folder_path} has been deleted successfully.")
    else:
        print(f"The folder {folder_path} does not exist.")  

class Connection:
    def __init__(self, conn, addr):
        self.conn = conn
        self.addr = addr

    def close(self):
        """断开连接"""
        self.conn.close()
        print(f"{self.addr[0]}:{self.addr[1]}断开连接")

    def send_msg(self, message):
        """发送信息"""
        self.conn.send(message.encode())

    def receive_msg(self, bufsize=1024):
        """接收信息"""
        data_received = self.conn.recv(bufsize).decode()
        return data_received


def handle_client(conn, addr, server):
    """单独处理每个客户端连接"""
    con = Connection(conn, addr)
    print(f"客户端 {addr[0]}:{addr[1]} 已连接")

    while True:
        try:
            msg = con.receive_msg(settings.buffer_size)
            print(f"收到客户端 {addr} 的消息: {msg}")

            if not msg:  # 防止客户端突然断开
                break

            if msg == 'quit':  # 客户端请求退出
                con.close()
                break

            text_en = translate(msg)
            # 生成图像路径并返回
            text_input(text_en)
            img_path = '/home/ubuntu/zhouzhi/SceneDreamer360/logs/4142dlo4/predict/e9zR4mvMWw7_99/pano_enhance.jpg'
            try:
                img_path = generate()  # 调用生成函数
                con.send_msg('找到了')
                time.sleep(1)
                server.send_img(con, img_path)
                folder_path = img_path.split('/pano_enhance')[0]
                print('图片路径是',img_path)
                print('要删除的路径是：',folder_path)
                delete_folder(folder_path)
            except Exception as e:
                con.send_msg('失败，请重新输入！')
                print(f"处理客户端 {addr} 的请求时出错: {e}")
        except Exception as e:
            print(f"客户端 {addr} 通信异常: {e}")
            break

    con.close()


if __name__ == '__main__':
    A_Server = Server()
    A_Server.bind()

    try:
        while True:
            print("等待客户端连接...")
            conn, addr = A_Server.socket.accept()  # 接收客户端连接
            # 为每个客户端启动一个线程
            client_thread = Thread(target=handle_client, args=(conn, addr, A_Server))
            client_thread.daemon = True  # 设置为守护线程，主程序退出时线程自动关闭
            client_thread.start()
    except KeyboardInterrupt:
        print("\n服务端正在关闭...")
    finally:
        A_Server.close()
