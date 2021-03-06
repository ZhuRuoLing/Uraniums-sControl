import json
import time
import socket

from mcdreforged.api.all import *

from .constant import *
from .crypto import Crypto
from .socket_server import cfg, service
from .udp_broadcast import udp_broadcast_receiver

config = DEFAULT_CONFIG.copy()
default_cfg = cfg.copy()
text_3: list


def on_load(server: PluginServerInterface, prev):
    service(server)
    global config
    config = server.load_config_simple(default_config=default_cfg)
    server.logger.info(config)
    udp_broadcast_receiver(server, config)
    pass


@new_thread("PlayerJoinEvent")
def on_player_joined(server: PluginServerInterface, player: str, info: Info):
    global config, text_3
    sock = socket.socket()
    if '[local]' in player:
        server.logger.info("Auth complete[local]:" + player)
        return
    endpoint = (config.get("qlink_ip"), config.get("qlink_port"))
    sock.settimeout(5.0)
    sock.connect(endpoint)
    _crypto = Crypto(config.get("qlink_crypto_key"))
    data = {
        "cmd": "WHITELIST_LIST",
        "load": [
            config.get("qlink_key")
        ]
    }
    sock.sendall((_crypto.encrypt(json.dumps(data)) + '\n').encode('utf-8'))
    data = sock.recv(BUF_SIZE)
    servers: list
    if data is not None:
        decrypted_data = _crypto.decrypt(data.decode("utf-8"))
        dictionary: dict
        dictionary = json.loads(decrypted_data)
        msg: str
        msg = dictionary.get("msg")
        if msg == "OK":
            servers = dictionary.get("load")
        else:
            server.execute("kick {} 与白名单服务器认证失败".format(player))
            return
    else:
        return

    def check_server(s, server_name: str, player_name: str) -> bool:
        """
        checks if the player in whitelist
        :param s: socket to send
        :param server_name: The name of server which will be tried
        :param player_name: player name
        :return: True: Success
        """
        _data = {
            "cmd": "WHITELIST_QUERY",
            "load": [
                server_name,
                player_name,
                config.get("qlink_key")
            ]
        }
        sock.sendall((_crypto.encrypt(json.dumps(_data)) + '\n').encode('utf-8'))
        _data = sock.recv(BUF_SIZE)

        if _data is not None:
            _decrypted_data = _crypto.decrypt(_data.decode("utf-8"))
            _dictionary: dict
            _dictionary = json.loads(_decrypted_data)
            _msg: str
            _msg = _dictionary.get("msg")
            if _msg == "OK":
                return True
            else:
                return False

    passed_server = []
    for name in servers:
        if check_server(sock, name, player_name=player):
            passed_server.append(name)
    if config.get("uses_whitelist") in passed_server:
        # let's show join motd
        name = config.get("name")
        text_1 = f"--------------- {name} ----------------"
        text_2 = "欢迎！点击下面的名字以进入对应服务器。"
        text_3 = []
        for i in passed_server:
            if i == config.get("uses_whitelist"):
                rtext = RText(i).set_color(RColor.yellow).set_hover_text(i)
            else:
                rtext = RText(i).set_color(RColor.aqua).set_hover_text(i).set_click_event(RAction.suggest_command,
                                                                                          f"/server {i}")
            rtext_list = RTextList("[", rtext, "]")
            text_3.append(rtext_list)
        sock.close()
        server_list = RTextList(*text_3)
        server.tell(player, text_1)
        server.tell(player, text_2)
        server.tell(player, "")
        server.tell(player, server_list)
        server.tell(player, "")
        return
    else:
        server.execute("kick {} 你不在白名单中".format(player))


def on_user_info(server: PluginServerInterface, info: Info):
    """
    send_time = json_dict.get("time")
            from_server = json_dict.get("server")
            from_player = json_dict.get("player")
            content = json_dict.get("content")
    """
    if not info.is_player:
        return
    message = {
        "time": int(time.time()),
        "server": config.get("name"),
        "player": info.player,
        "content": info.content
    }
    json_text = json.dumps(message)
    data = json_text.encode("utf-8")
    s = socket.socket(type=socket.SOCK_DGRAM)
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    s.bind(("0.0.0.0", 10086))
    s.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_TTL, 64)
    s.setsockopt(socket.IPPROTO_IP,
                 socket.IP_ADD_MEMBERSHIP,
                 socket.inet_aton("224.114.51.4") + socket.inet_aton("0.0.0.0"))
    s.setblocking(True)
    s.sendto(data, ("224.114.51.4", 10086))
    s.close()

