import json
from socket import socket

from mcdreforged.api.all import *

from .constant import *
from .crypto import Crypto
from .socket_server import cfg, service

config = DEFAULT_CONFIG.copy()
default_cfg = cfg.copy()


def on_load(server: PluginServerInterface, prev):
    service(server)
    global config
    config = server.load_config_simple(default_config=default_cfg)
    server.logger.info(config)
    pass


@new_thread("PlayerJoinEvent")
def on_player_joined(server: PluginServerInterface, player: str, info: Info):
    global config
    sock = socket()
    if '[local]' in player:
        server.logger.info("Auth complete[local]:" + player)
        return
    endpoint = (config.get("qlink_ip"), config.get("qlink_port"))
    sock.settimeout(5.0)
    sock.connect(endpoint)
    crypter = Crypto(config.get("qlink_crypto_key"))
    data = {
        "cmd": "WHITELIST_QUERY",
        "load": [
            config.get("uses_whitelist"),
            player,
            config.get("qlink_key")
        ]
    }
    sock.sendall((crypter.encrypt(json.dumps(data)) + '\n').encode('utf-8'))
    data = sock.recv(BUF_SIZE)
    sock.close()
    if data is not None:
        decrypted_data = crypter.decrypt(data.decode("utf-8"))
        ddict: dict
        ddict = json.loads(decrypted_data)
        msg: str
        msg = ddict.get("msg")
        if msg == "OK":
            server.logger.info("Auth complete:" + player)
            return
        else:
            server.execute("kick {} 恁不在白名单中".format(player))
            return
