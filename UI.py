
import tkinter
import tkinter.messagebox
import tkinter.simpledialog
from datetime import datetime

mycolor = "black"
thickness = 1
chatindex = 1.0

def paint(event):
    x1, y1 = ( event.x-thickness ), ( event.y-thickness )
    x2, y2 = ( event.x+thickness ), ( event.y+thickness )
    canvas.create_oval(x1, y1, x2, y2, fill=mycolor, outline=mycolor)


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


def start_timer():
    global elapsed_time
    elapsed_time = 0
    start_button["state"] = tkinter.DISABLED
    update_timer()


def update_timer():
    global elapsed_time
    elapsed_time += 0.1
    lefttime = round(90 - elapsed_time, 1)
    timer_label.config(text=f"남은시간 : {lefttime} seconds")
    timer_label.after(100, update_timer)
    if elapsed_time == 90 or lefttime == 0:
        start_button["state"] = tkinter.NORMAL

def dialog():
    chat = entry.get()
    if chat != "":
        textwindow.insert(chatindex, chat+"\n")
    entry.delete(0, 'end')

window = tkinter.Tk()
window.geometry("1280x1080+100+100")
canvas = tkinter.Canvas(window, bg="white", width=800, height=640)
canvas.place(x=400, y=00, width=800, height=800)
#왼쪽 마우스를 누르면 그려지도록 함
canvas.bind("<B1-Motion>", paint)

#"빨간색"버튼을 누르면 change_color 함수를 통해 색 변경
button = tkinter.Button(window, text="검정색",command=change_color_black)
button.place(x=0, y=50,width=50, height=30)
button1 = tkinter.Button(window, text="빨간색",command=change_color_red)
button1.place(x=50, y=50,width=50, height=30)
button2 = tkinter.Button(window, text="파란색",command=change_color_blue)
button2.place(x=100, y=50,width=50, height=30)
button3 = tkinter.Button(window, text="초록색",command=change_color_green)
button3.place(x=150, y=50,width=50, height=30)
button4 = tkinter.Button(window, text="굵게",command=thickness_thicker)
button4.place(x=100, y=80, width=50, height=30)
button5 = tkinter.Button(window, text="얇게",command=thickness_thinner)
button5.place(x=150, y=80, width=50, height=30)
button6 = tkinter.Button(window, text="전체 지우기",command=clear)
button6.place(x=50, y=110, width=100, height=30)
button7 = tkinter.Button(window, text="지우개",command=erase)
button7.place(x=150, y=110, width=50, height=30)
button8 = tkinter.Button(window, text="보내기",command=dialog)
button8.place(x=300, y=610, width=50, height=30)

label = tkinter.Label(window, text="굵기 : " + str(thickness))
label.place(x=50, y=80, width=50, height=30)

timer_label = tkinter.Label(window, font=("Arial", 20), fg="black")
timer_label.place(x=0, y=250, width=300, height=50)

start_button = tkinter.Button(window, text="Start Timer", command=start_timer)
start_button.place(x=0, y=200, width=230, height=30)

entry = tkinter.Entry(window)
entry.place(x=0, y=610, width=300, height=30)

textwindow = tkinter.Text(window)
textwindow.place(x=0, y=300, width=350, height=300)

window.mainloop()
