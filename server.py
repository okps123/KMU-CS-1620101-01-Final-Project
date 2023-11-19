import socket
import threading
import time
from enum import Enum
from common.packet import Packet, PacketType
from common.serdes import serialize, deserialize

# 클라이언트 정보를 담는 클래스
class Client:
    def __init__(self, id: int, address: str, socket: socket.socket):
        self.id = id
        self.address = address
        self.socket = socket
        self.nickname = None
        self.score = 0
        self.is_drawer = False

    def is_joined(self):
        return self.nickname is not None

    def join(self, nickname: str):
        self.nickname = nickname

    def __str__(self):
        return f'Client(id={self.id}, socket={self.socket}, nickname={self.nickname})'

class Game:
    MIN_PARTICIPANTS = 2
    
    joined_clients: list = []

    def __init__(self):
        self.id = time.time()
        self.state = None
        self.drawer = None
        self.word = None
        self.start_at = 0

        print(f'게임이 생성되었습니다.')

    def join(self, client: Client):
        self.joined_clients.append(client)
        print(f'{client.nickname}님이 게임에 참가하였습니다.')

        if (len(self.joined_clients) >= self.MIN_PARTICIPANTS):
            self.start_at = time.time()
            print(f'최소 인원이 모였습니다. 게임을 시작합니다.')
    
    def leave(self, client: Client):
        self.joined_clients.remove(client)
        print(f'{client.nickname}님이 게임에서 나갔습니다.')

        if (len(self.joined_clients) < self.MIN_PARTICIPANTS):
            print(f"최소 인원보다 적어 게임을 종료합니다.")

game = Game()

# 클라이언트 리스트
clients: list = []

# 서버의 IP 주소와 포트 번호
SERVER_IP = '127.0.0.1'
SERVER_PORT = 12345

# 서버 소켓 생성
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# TIME_WAIT 상태의 소켓에 재연결이 가능하도록 설정 (SO_REUSEADDR)
server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

# 서버 IP 주소와 포트 번호를 바인딩
server_socket.bind((SERVER_IP, SERVER_PORT))

# 클라이언트의 연결을 받을 수 있도록 대기
server_socket.listen()

print('서버가 시작되었습니다.')

# 클라이언트와 통신하는 함수
def handle_client(client: Client):
    print(f'클라이언트 연결됨: {client.address}')

    while True:
        # 클라이언트로부터 데이터 수신
        data = client.socket.recv(1024)
        if not data:
            break

        # 데이터 역직렬화
        message = deserialize(data)

        # print(f'클라이언트로부터 받은 메시지: {message}')

        # 받은 메시지의 타입에 따라 처리
        handle_client_message(client, message)

    # 클라이언트와의 연결 종료
    if (client.is_joined()):
        handle_client_leave(client)

    client.socket.close()
    clients.remove(client)

    print(f'클라이언트 연결 종료: {client.address}')

def handle_client_message(client: Client, message: any):
    if message.type == PacketType.CLIENT_JOIN:
        handle_client_join(client, message)
        
    elif message.type == PacketType.CLIENT_LEAVE:
        handle_client_leave(client)

    elif message.type == PacketType.CHAT:
        print(f'{client.nickname}: {message.data}')
        
        packet = Packet(PacketType.CHAT, {
            'id': client.id,
            'nickname': client.nickname,
            'message': message.data,
        })
        broadcast_message(packet)

def handle_client_join(client: Client, message: any):
    client.join(nickname=message.data['nickname'])
    game.join(client)

    packet = Packet(PacketType.CLIENT_JOIN, { 'id': client.id, 'nickname': client.nickname, })
    broadcast_message(packet)

def handle_client_leave(client: Client):
    game.leave(client)

    packet = Packet(PacketType.CLIENT_LEAVE, { 'id': client.id, })
    broadcast_message(packet)

# 모든 클라이언트에게 메시지를 브로드캐스트하는 함수
def broadcast_message(message):
    data = serialize(message)

    for client in clients:
        client.socket.sendall(data)

def exit_server():
    print('서버를 종료합니다.')

    # 모든 클라이언트 소켓 닫기
    for client in clients:
        client.socket.close()

    # 서버 소켓 닫기
    server_socket.close()

try:
    while True:
        # 클라이언트의 연결 요청을 수락
        client_socket, client_address = server_socket.accept()

        # 클라이언트 소켓을 리스트에 추가
        client = Client(
                id=len(clients) + 1,
                address=client_address,
                socket=client_socket
        )
        
        clients.append(client)

        # 클라이언트와 통신하는 스레드 생성
        client_thread = threading.Thread(target=handle_client,args=(client, ))
        client_thread.start()

except Exception as e:
    exit_server()
except KeyboardInterrupt as e:
    exit_server()