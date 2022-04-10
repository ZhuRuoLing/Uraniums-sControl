import json
import socket

from mcdreforged.api.all import *


@new_thread("UdpBroadcastReceiver")
def udp_broadcast_receiver(server: PluginServerInterface):
    server.logger.info("Started Broadcast receiver thread")
    s = socket.socket(type=socket.SOCK_DGRAM)
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    s.bind(("0.0.0.0", 10086))
    s.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_TTL, 64)
    s.setsockopt(socket.IPPROTO_IP,
                 socket.IP_ADD_MEMBERSHIP,
                 socket.inet_aton("224.114.51.4") + socket.inet_aton("0.0.0.0"))
    s.setblocking(True)
    while True:
        try:
            data, address = s.recvfrom(114514)
            json_str = data.decode("utf-8")
            json_dict: dict = json.loads(json_str)
            send_time = json_dict.get("time")
            from_server = json_dict.get("server")
            from_player = json_dict.get("player")
            content = json_dict.get("content")
            server_ = RText(from_server).set_color(RColor.yellow).set_styles(RStyle.bold)
            player = RText(from_player).set_color(RColor.green)

            final_rtext = RTextList(send_time, " <", player,
                                    RText("[").set_color(RColor.green),
                                    server_,
                                    RText("]> ").set_color(RColor.green)
                                    , content)
            server.broadcast(final_rtext)
        except Exception as e:
            server.logger.info(str(e))
    # 224.114.51.4:10086
