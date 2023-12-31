import socket
import threading
import tkinter
import tkinter.messagebox
import tkinter.simpledialog
from datetime import datetime
from common.packet import Packet, PacketType
from common.serdes import serialize, deserialize

mycolor = "black"
thickness = 1
chatindex = 1.0

# 서버 주소와 포트 번호
server_address = ('localhost', 12345)

# 소켓 생성
client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# 서버에 연결
client_socket.connect(server_address)

def receive_message():
    while True:
        # 서버로부터 응답 받기
        data = client_socket.recv(1024)
        message = deserialize(data)
        
        # 받은 메시지의 타입에 따라 처리
        if message.type == PacketType.CLIENT_JOIN:
            textwindow.insert(1.0, message.data['nickname'] + "님이 입장하셨습니다.\n")
        elif message.type == PacketType.CLIENT_LEAVE:
            textwindow.insert(1.0, message.data['nickname'] + "님이 퇴장하셨습니다.\n")
        elif message.type == PacketType.CLIENT_JOIN_CONFIRM:
            global clientId
            clientId = message.data['id']
            textwindow.insert(1.0, message.data['nickname'] + "님이 입장하셨습니다.\n")
            print(f'내 클라이언트 아이디: {clientId}')

        elif message.type == PacketType.CHAT:
            id = message.data['id']
            name = message.data['nickname']
            text = message.data['message']

            textwindow.insert(1.0, name + ": " + text + "\n")

        elif message.type == PacketType.DRAW:
            draw_canvas(message.data[0], message.data[1], message.data[2], message.data[3])
        elif message.type == PacketType.CLEAR:
            clear()
        # 이부분 메세지 데이터에서 단어만 뽑아서 message.data대신 넣으시면 됩니다. data가 정확히 어떻게 구성된건지 헷갈려서 일단은 놔뒀어요.
        elif message.type == PacketType.ROUND_START:
            textwindow.insert(1.0, "라운드가 시작됐습니다.\n")
            clear()

            if clientId == message.data['drawer_id']:
                textwindow.insert(1.0, "그림을 그릴 차례입니다. 제시어는 " + message.data['word'] + "입니다.\n")
                answer_entry.delete(1.0, tkinter.END)
                answer_entry.insert(1.0, "제시어: " + message.data['word'])
            else:
                textwindow.insert(1.0, "그림을 맞춰보세요.\n")
        elif message.type == PacketType.ROUND_END:
            textwindow.insert(1.0, "라운드가 끝났습니다.\n")
        elif message.type == PacketType.GAME_END:
            textwindow.insert(1.0, "게임이 끝났습니다.\n")
        elif message.type == PacketType.GUESS_CORRECT:
            textwindow.insert(1.0, message.data['nickname'] + "님이 맞추셨습니다. 정답은 " + message.data['word'] + "입니다.\n")


        # 응답 출력
        print(message)



def paint(event):
    message = [event.x, event.y, thickness, mycolor]
    packet = Packet(PacketType.DRAW, message)
    data = serialize(packet)
    client_socket.sendall(data)

def draw_canvas(x, y, thickness, color):
    x1, y1 = (x - thickness), (y - thickness)
    x2, y2 = (x + thickness), (y + thickness)
    canvas.create_oval(x1, y1, x2, y2, fill=color, outline=color)

def erase():
    global mycolor
    mycolor = "white"

def change_color_black():
    global mycolor
    mycolor="black"

def change_color_red():
    global mycolor
    mycolor="red"

def change_color_blue():
    global mycolor
    mycolor="blue"

def change_color_green():
    global mycolor
    mycolor="green"

def thickness_thicker():
    global thickness
    if thickness <= 9:
        thickness += 1
    label["text"] = "굵기 : " + str(thickness)

def thickness_thinner():
    global thickness
    if thickness >=2:
        thickness -= 1
    label["text"] = "굵기 : " + str(thickness)

def clear():
    canvas.delete("all")

def send_clear():
    packet = Packet(PacketType.CLEAR, {})
    data = serialize(packet)
    client_socket.sendall(data)

def start_timer():
    global elapsed_time
    elapsed_time = 0
    start_button["state"] = tkinter.DISABLED
    update_timer()
    message = "round start"
    packet = Packet(PacketType.ROUND_START, message)
    data = serialize(packet)
    client_socket.sendall(data)
    packet = Packet(PacketType.SET_LEFT_TIME, "set left time to 90s")
    data = serialize(packet)
    client_socket.sendall(data)
    print(message)
    print("set left time to 90s")


def update_timer():
    global elapsed_time
    elapsed_time += 1
    lefttime = round(90 - elapsed_time, 1)
    timer_label.config(text=f"남은시간 : {lefttime} seconds")
    timer_label.after(1000, update_timer)
    if elapsed_time == 90 or lefttime == 0:
        start_button["state"] = tkinter.NORMAL

def dialog():
    chat = entry.get()
    if chat != "":
        packet = Packet(PacketType.CHAT, chat)
        data = serialize(packet)
        client_socket.sendall(data)

    entry.delete(0, 'end')

name = input("이름을 입력하세요: ")
packet = Packet(PacketType.CLIENT_JOIN, {'nickname': name})
data = serialize(packet)
client_socket.sendall(data)

window = tkinter.Tk()
window.geometry("1280x1080+100+100")
canvas = tkinter.Canvas(window, bg="white", width=800, height=640)
canvas.place(x=400, y=00, width=800, height=800)
# 왼쪽 마우스를 누르면 그려지도록 함
canvas.bind("<B1-Motion>", paint)
# "빨간색"버튼을 누르면 change_color 함수를 통해 색 변경
button = tkinter.Button(window, text="검정색", command=change_color_black)
button.place(x=0, y=50, width=50, height=30)
button1 = tkinter.Button(window, text="빨간색", command=change_color_red)
button1.place(x=50, y=50, width=50, height=30)
button2 = tkinter.Button(window, text="파란색", command=change_color_blue)
button2.place(x=100, y=50, width=50, height=30)
button3 = tkinter.Button(window, text="초록색", command=change_color_green)
button3.place(x=150, y=50, width=50, height=30)
button4 = tkinter.Button(window, text="굵게", command=thickness_thicker)
button4.place(x=100, y=80, width=50, height=30)
button5 = tkinter.Button(window, text="얇게", command=thickness_thinner)
button5.place(x=150, y=80, width=50, height=30)
button6 = tkinter.Button(window, text="전체 지우기", command=send_clear)
button6.place(x=50, y=110, width=100, height=30)
button7 = tkinter.Button(window, text="지우개", command=erase)
button7.place(x=150, y=110, width=50, height=30)
button8 = tkinter.Button(window, text="보내기", command=dialog)
button8.place(x=300, y=610, width=50, height=30)

label = tkinter.Label(window, text="굵기 : " + str(thickness))
label.place(x=50, y=80, width=50, height=30)

timer_label = tkinter.Label(window, font=("Arial", 20), fg="black")
timer_label.place(x=0, y=250, width=300, height=50)

start_button = tkinter.Button(window, text="Start Timer", command=start_timer)
start_button.place(x=0, y=200, width=230, height=30)

entry = tkinter.Entry(window)
entry.place(x=0, y=610, width=300, height=30)

answer_entry = tkinter.Text(window, state="normal")
answer_entry.place(x=0, y=150, width=230, height=40)


textwindow = tkinter.Text(window, font=("Arial", 15))
textwindow.place(x=0, y=300, width=350, height=300)

# 메시지 수신을 위한 스레드 생성 및 시작
receive_thread = threading.Thread(target=receive_message)
receive_thread.start()

window.mainloop()

while True:
    # 메시지 전송
    message = input()
    packet = Packet(PacketType.CHAT, message)
    data = serialize(packet)
    client_socket.sendall(data)
