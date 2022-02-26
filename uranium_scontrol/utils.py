import socket
from .constant import BUF_SIZE

result = None


def socket_receive(s: socket.socket) -> str:
    global result
    sock = s
    result: str
    while True:
        tmp = sock.recv(BUF_SIZE).decode("utf-8")
        result += tmp
        if tmp.endswith("\n"):
            break
    return result
