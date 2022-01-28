import json
import socketserver
import time

from mcdreforged.api.decorator import new_thread
from mcdreforged.minecraft.rtext import RText, RColor
from mcdreforged.plugin.server_interface import PluginServerInterface
from .crypto import *
from .constant import *

gl_server: PluginServerInterface
cfg = DEFAULT_CONFIG.copy()


class ThreadedTCPRequestHandler(socketserver.BaseRequestHandler):
    def handle(self):
        global gl_server
        if gl_server is None:
            return
        data = self.request.recv(BUF_SIZE)
        crypto = Crypto(cfg.get("key"))
        if data is not None:
            decrypted_data = crypto.decrypt(data.decode("utf-8"))
            ddict: dict
            ddict = json.loads(decrypted_data)
            cmd: str
            cmd = ddict.get("cmd")
            if cmd == "ANNOUNCE":
                content = ddict.get("load")[0]
                gl_server.broadcast(RText(content).set_color(RColor.aqua))
                dt = OK_DATA.copy()
                self.request.sendall(crypto.encrypt(json.dumps(dt)).encode("utf-8"))
                return
            elif cmd == "STOP":
                gl_server.broadcast(RText("服务器即将关闭。").set_color(RColor.aqua))
                time.sleep(5)
                content = ddict.get("load")[0]
                if content == "true":
                    gl_server.stop_exit()
                else:
                    gl_server.stop()
                dt = OK_DATA.copy()
                self.request.sendall(crypto.encrypt(json.dumps(dt)).encode("utf-8"))
                return
            elif cmd == "EXECUTE_COMMAND":
                type_ = ddict.get("load")[0]
                if type_ == "minecraft":
                    gl_server.execute(ddict.get("load")[1])
                else:
                    gl_server.execute_command(ddict.get("load")[1])
                dt = OK_DATA.copy()
                self.request.sendall(crypto.encrypt(json.dumps(dt)).encode("utf-8"))
            else:
                pass


class ThreadedTCPServer(socketserver.ThreadingMixIn,
                        socketserver.TCPServer):  # 继承ThreadingMixIn表示使用多线程处理request，注意这两个类的继承顺序不能变
    pass


@new_thread("UraniumSocketServer")
def service(server: PluginServerInterface):
    global gl_server, cfg
    gl_server = server
    cfg = server.load_config_simple(default_config=DEFAULT_CONFIG.copy())
    host, port = "0.0.0.0", cfg.get("port")
    socket_server = ThreadedTCPServer((host, port), ThreadedTCPRequestHandler)
    socket_server.serve_forever()
