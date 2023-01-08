import json
from socket import socket

from data_types import Long
from packet.packets.handshake.C0x0 import C0x0 as HC0x0
from packet.packets.status.C0x0 import C0x0 as SC0x0
from packet.packets.status.C0x1 import C0x1 as SC0x1
from packet.packets.status.S0x0 import S0x0 as SS0x0
from packet.packets.status.S0x1 import S0x1 as SS0x1
from packet.raw_packet import RawPacket

'''
author: hsn8086
date: 01/06/2023(MM/DD/YY)
'''

status_list = {}  # 状态列表


def client_recv(conn_: socket, addr_: tuple):
    global status_list  # 声明status为全局变量
    while True:  # 进入接收循环
        try:
            rp = RawPacket(conn_)  # 获取原始包

            if len(bytes(rp)) == 0:  # 如果无法接收到数据包则停止运行
                raise ''

        except:
            conn_.close()  # 关闭连接
            status_list[str(addr_)] = 'handshake'  # 连接状态初始化
            break

        if str(addr_) not in status_list:  # 判断键是否存在
            status_list[str(addr_)] = 'handshake'  # 连接状态初始化

        if status_list[str(addr_)] == 'handshake':  # 判断连接状态
            if int(rp.id) == 0:  # 判断包id
                p = HC0x0()
                p.from_raw_packet(rp)  # 获取handshake0x00包
                protocol_ver, recv_addr, recv_port, status = p.read()  # 读取包
                if int(status) == 1:
                    status_list[str(addr_)] = 'status'  # 切换状态
                continue  # 结束本轮
        if status_list[str(addr_)] == 'status':
            if int(rp.id) == 0:
                p = SC0x0()
                p.from_raw_packet(rp)  # 读取status0x00包
                rt_p = SS0x0()
                rt_p += json.dumps({
                    "version": {
                        "name": "1.19.3",
                        "protocol": 761
                    },
                    "players": {
                        "max": 100,
                        "online": 5,
                        "sample": [
                            {
                                "name": "thinkofdeath",
                                "id": "4566e69f-c907-48ee-8d71-d7ba5aa00d20"
                            }
                        ]
                    },
                    "description": {
                        "text": "Hello world"
                    },
                    "favicon": "data:image/png;base64,<data>",
                    "previewsChat": True
                })  # 加入数据

                conn_.send(bytes(rt_p))  # 返回数据
                continue
            if int(rp.id) == 1:
                '''
                其实这段代码是非常多余的...
                正常来说
                conn_.send(bytes(rp))  # 返回数据
                continue
                就行,不过这里为了展示包的结构,特有分开来写
                '''
                p = SC0x1()
                p.from_raw_packet(rp)  # 读取status0x01包
                payload = p.read()[0]
                rt_p = SS0x1()
                rt_p += Long(payload)
                conn_.send(bytes(rt_p))  # 返回数据
                continue


if __name__ == '__main__':  # 程序入口
    s = socket()  # 创建socket对象

    s.bind(("0.0.0.0", 25565))  # 绑定ip
    s.listen(2000)  # 监听
    while True:
        conn, addr = s.accept()  # 建立连接
        client_recv(conn, addr)  # 进入处理函数
