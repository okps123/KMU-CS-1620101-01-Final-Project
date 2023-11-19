
import socket
from common.packet import Packet, PacketType
from common.serdes import serialize, deserialize

# 서버 주소와 포트 번호
server_address = ('localhost', 12345)

# 소켓 생성
client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# 서버에 연결
client_socket.connect(server_address)

# 메시지 전송
message = input()
packet = Packet(PacketType.CHAT, message)

data = serialize(packet)

client_socket.sendall(data)

# 서버로부터 응답 받기
data = client_socket.recv(1024)
message = deserialize(data)

# 응답 출력
print('서버로부터 받은 응답:', message)

# 소켓 닫기
client_socket.close()
