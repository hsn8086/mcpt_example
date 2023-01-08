import copy
import json
import random
import time
from socket import socket

from data_types import VarInt, UnsignedShort, Long, Byte
from packet.packets.handshake.C0x0 import C0x0 as HC0x0
from packet.packets.status.C0x0 import C0x0 as SC0x0
from packet.packets.status.S0x0 import S0x0 as SS0x0
from packet.packets.status.C0x1 import C0x1 as SC0x1
from packet.packets.status.S0x1 import S0x1 as SS0x1
from packet.raw_packet import RawPacket


def get_motd(addr: tuple[str, int] = None):
    if addr is None:  # 判断参数是否为空
        addr_ = ("127.0.0.1", 25565)  # 使用默认参数
    else:
        addr_ = copy.copy(addr)
    s = socket()  # 创建socket对象
    s.connect(addr_)  # 连接服务器

    hc0x0 = HC0x0()  # 创建包handshakeC0x0
    hc0x0 += VarInt(761)  # 协议版本号
    hc0x0 += addr_[0]  # 服务器地址
    hc0x0 += UnsignedShort(addr_[1])  # 服务器端口号
    hc0x0 += Byte([1])  # 接下来的状态
    s.send(bytes(hc0x0))  # 发送包

    s.send(bytes(SC0x0()))  # 发送包statusC0x0

    rp_ss0x0 = RawPacket(s)  # 接收原始包statusS0x0
    ss0x0 = SS0x0()
    ss0x0.from_raw_packet(rp_ss0x0)  # 解析包
    json_str = ss0x0.read()[0]  # 读取参数

    sc0x1 = SC0x1()  # 创建statusC0x1
    payload = Long(random.randint(114514, 1919810))  # 创建payload
    sc0x1 += payload
    s.send(bytes(sc0x1))  # 发送statusC0x1
    s_time = time.time()  # 开始计时

    rp_ss0x1 = RawPacket(s)  # 接收原始包statusS0x1
    delay = time.time() - s_time  # 计算延迟
    ss0x1 = SS0x1()
    ss0x1.from_raw_packet(rp_ss0x1)  # 解析包
    recv_payload = ss0x1.read()[0]  # 获取参数
    if recv_payload == payload:  # 比较参数
        return int(delay * 1000), json.loads(json_str)  # 返回数据


if __name__ == '__main__':
    print(get_motd(('ZQAT.top', 25565)))
