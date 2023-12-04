import socket
import threading
import time
import random
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

    drawer_index: int = None
    current_drawer: Client = None
    current_word: str = None
    ronud_start_at: float = None

    word_set: set = set(['사과', '바나나', '포도', '수박', '딸기', '키위', '오렌지', '레몬', '망고', '복숭아'])

    def __init__(self):
        self.id = time.time()

    def join(self, client: Client):
        # 다른 클라이언트에게 새로운 클라이언트 정보 전송
        self.send_all(Packet(PacketType.CLIENT_JOIN, {
            'id': client.id,
            'nickname': client.nickname,
        }))

        self.joined_clients.append(client)

        # 게임에 참가한 클라이언트에게 게임 참가 확인 메시지 전송
        self.send(client, Packet(PacketType.CLIENT_JOIN_CONFIRM, {
            'id': client.id,
            'nickname': client.nickname,
        }))

        print(f'{client.nickname}님이 게임에 참가하였습니다.')

        time.sleep(0.1)

        if (len(self.joined_clients) >= self.MIN_PARTICIPANTS):
            print(f'최소 인원이 모였습니다. 게임을 시작합니다.')
            self.start_game()
    
    def leave(self, client: Client):
        self.joined_clients.remove(client)
        self.send_all(Packet(PacketType.CLIENT_LEAVE, { 'id': client.id, }))
        print(f'{client.nickname}님이 게임에서 나갔습니다.')

        if (len(self.joined_clients) < self.MIN_PARTICIPANTS):
            print(f"최소 인원보다 적어 게임을 종료합니다.")

    def start_game(self):
        print(f'게임을 시작합니다.')
        self.start_at = time.time()
        self.send_all(Packet(PacketType.GAME_START, {}))

        self.init_round()
        self.start_round()

    def init_round(self):
        self.current_drawer = None
        self.current_word = None
        self.drawer_index = -1

    def start_round(self):
        self.drawer_index += 1
        if (self.drawer_index >= len(self.joined_clients)):
            print(f'모든 참가자가 한 번씩 그렸습니다. 게임을 종료합니다.')
            self.send_all(Packet(PacketType.GAME_END, {}))
            return
        
        drawer = self.joined_clients[self.drawer_index]
        self.current_drawer = drawer

        word = random.choice(list(self.word_set))
        self.current_word = word

        self.ronud_start_at = time.time()

        print(f'{drawer.nickname}님이 그림을 그립니다. (단어: {word})')

        time.sleep(0.1)

        self.send_all(Packet(PacketType.ROUND_START, {
            'drawer_id': drawer.id,
            'word': word,
            'start_time': self.ronud_start_at,
        }))
        self.start_round_timer(start_time=self.ronud_start_at)
    
    def end_round(self):
        print(f'라운드를 종료합니다.')
        self.send_all(Packet(PacketType.ROUND_END, {}))

        time.sleep(1)
        self.start_round()

    def guess(self, client: Client, message: any):
        if (self.current_drawer == client):
            return
        
        if (self.current_word == message):
            print(f'{client.nickname}님이 정답을 맞췄습니다.')
            self.send_all(Packet(PacketType.GUESS_CORRECT, {
                'id': client.id,
                'nickname': client.nickname,
                'word': self.current_word,
            }))
            self.end_round()
        else:
            print(f'{client.nickname}님이 정답을 맞추지 못했습니다.')

    def draw(self, client: Client, message: any):
        # 그리는 중인 클라이언트가 아니면 무시
        if (self.current_drawer != client):
            return
        
        self.send_all(Packet(PacketType.DRAW, message))

    def clear(self, client: Client, message: any):
        # 그리는 중인 클라이언트가 아니면 무시
        if (self.current_drawer != client):
            return
        
        self.send_all(Packet(PacketType.CLEAR, {}))

    def start_round_timer(self, start_time: float, round_time: int = 60):
        def callback():
            left_time = round_time - (time.time() - start_time)
            print(f'남은 시간: {left_time}초')
            self.end_round()

        threading.Timer(round_time, callback).start()
    
    def send(self, client: Client, packet: Packet):
        data = serialize(packet)
        client.socket.sendall(data)

    def send_all(self, packet: Packet):
        data = serialize(packet)
        for client in self.joined_clients:
            # print(f'{client.nickname}에게 메시지 전송: {packet}')
            client.socket.sendall(data)

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
        if not data: # 클라이언트와 연결이 끊어지면 data는 빈 문자열
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
        handle_client_chat(client, message)

    elif message.type == PacketType.DRAW:
        handle_client_draw(client, message)
    
    elif message.type == PacketType.CLEAR:
        handle_client_clear(client, message)

def handle_client_join(client: Client, message: any):
    client.join(nickname=message.data['nickname'])
    game.join(client)

def handle_client_leave(client: Client):
    game.leave(client)

def handle_client_chat(client: Client, message: any):
    print(f'{client.nickname}: {message.data}')

    packet = Packet(PacketType.CHAT, {
        'id': client.id,
        'nickname': client.nickname,
        'message': message.data,
    })
    game.send_all(packet)
    game.guess(client, message.data)

def handle_client_draw(client: Client, message: any):
    game.draw(client, message.data)

def handle_client_clear(client: Client, message: any):
    game.clear(client, message.data)

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