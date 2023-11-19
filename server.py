
import socket
import threading
from common.serdes import serialize, deserialize

# 클라이언트 소켓 리스트
client_sockets = []

# 서버의 IP 주소와 포트 번호
SERVER_IP = '127.0.0.1'
SERVER_PORT = 12345

# 서버 소켓 생성
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# 서버 IP 주소와 포트 번호를 바인딩
server_socket.bind((SERVER_IP, SERVER_PORT))

# 클라이언트의 연결을 받을 수 있도록 대기
server_socket.listen()

print('서버가 시작되었습니다.')

# 클라이언트와 통신하는 함수
def handle_client(client_socket, client_address):
    print(f'클라이언트 연결됨: {client_address}')

    while True:
        # 클라이언트로부터 데이터 수신
        data = client_socket.recv(1024)
        if not data:
            break

        # 데이터 역직렬화
        message = deserialize(data)

        print(f'클라이언트로부터 받은 데이터: {message}')

        # 받은 데이터를 클라이언트에게 다시 전송
        broadcast_message(message)

    # 클라이언트와의 연결 종료
    client_socket.close()
    client_sockets.remove(client_socket)

    print(f'클라이언트 연결 종료: {client_address}')

# 모든 클라이언트에게 메시지를 브로드캐스트하는 함수
def broadcast_message(message):
    data = serialize(message)

    for client_socket in client_sockets:
        client_socket.sendall(data)

try:
    while True:
        # 클라이언트의 연결 요청을 수락
        client_socket, client_address = server_socket.accept()

        # 클라이언트 소켓을 리스트에 추가
        client_sockets.append(client_socket)

        # 클라이언트와 통신하는 스레드 생성
        client_thread = threading.Thread(target=handle_client, args=(client_socket, client_address))
        client_thread.start()
except KeyboardInterrupt:
    print('서버를 종료합니다.')

    # 모든 클라이언트 소켓 닫기
    for client_socket in client_sockets:
        client_socket.close()

    # 서버 소켓 닫기
    server_socket.close()