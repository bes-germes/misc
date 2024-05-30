from tkinter import *
import json
import time
import subprocess
from PIL import Image, ImageTk
import numpy as np

prev_x = None
prev_y = None
res_velocity = None
res_coeff = None
Plane = []
point1 = {}
point2 = {}


def erase():
    global prev_x
    global prev_y
    global res_points
    global res_velocity
    global res_coeff
    global Plane
    global point1
    global point2

    canvas.delete("all")
    prev_x = None
    prev_y = None
    res_points = None
    res_velocity = None
    res_coeff = None
    Plane = []
    point1 = {}
    point2 = {}

    lbl_rock_1.config(
        text="Попадание обычной ракетой: {неизвестно, запустите симуляцию}"
    )
    lbl_rock_2.config(text="Попадание fuzzy-ракетой: {неизвестно, запустите симуляцию}")



def requestPointToNPPoint(p):
    return np.array([[p["x"]], [p["y"]]], np.float64)


def rocket():
    def b1(event):
        global prev_x, prev_y
        global point1, point2
        x = event.x
        y = event.y
        if prev_x:
            canvas.create_line(
                prev_x, prev_y, x, y, tags="all", dash=(10, 2), arrow=LAST, fill="GREEN"
            )
            point1 = {"x": prev_x, "y": prev_y}
            point2 = {"x": x, "y": y}
            x = None
            y = None
        prev_x = x
        prev_y = y

    canvas.bind("<Button-1>", b1)


def plane():
    global Plane

    def b1(event):
        x = event.x
        y = event.y
        canvas.create_oval(
            x - 5.0,
            y + 5.0,
            x + 5.0,
            y - 5.0,
            tags="all",
            outline="white",
            fill="ORANGE",
        )

        point = {"x": x, "y": y}
        Plane.append(point)

    canvas.bind("<Button-1>", b1)


def start():
    global res_points
    global res_velocity
    global res_coeff
    global Plane
    global point1
    global point2

    res_points = points.get()
    res_points = int(res_points)

    res_velocity = velocity.get()
    res_velocity = int(res_velocity)

    res_coeff = coeff.get()
    res_coeff = int(res_coeff)

    AircraftPoints = {
        "AircraftPoints": Plane,
        "Missiles": {
            "Defuzzification": "Centroid",
            "Direction": point2,
            "Inference": "Max-Prod",
            "LaunchPoint": point1,
            "PropCoeff": res_coeff,
            "VelocityModule": res_velocity,
        },
        "StepsCount": res_points,
    }

    with open("ImitationRequest.json", "w") as ap:
        ap.write(json.dumps(AircraftPoints, ensure_ascii=False))

    subprocess.run(["python", "calculations.py"])

    with open("ImitationResponse.json", "r") as IR:
        data = json.load(IR)

    curvesBasicPoints = np.hstack(
        tuple(map(requestPointToNPPoint, data["AircraftTrajectory"]))
    )
    for i in range(res_points - 5):
        x = curvesBasicPoints[0][i]
        y = curvesBasicPoints[1][i]
        canvas.create_oval(
            x - 1.0,
            y + 1.0,
            x + 1.0,
            y - 1.0,
            tags="all",
            outline="ORANGE",
            fill="ORANGE",
        )

    settings = data["UsualMissile"]
    curvesUsual = np.hstack(tuple(map(requestPointToNPPoint, settings["Trajectory"])))
    UsualP = np.shape(curvesUsual)
    for i in range(UsualP[1] - 1):
        x = curvesUsual[0][i]
        y = curvesUsual[1][i]
        canvas.create_oval(
            x - 1.0,
            y + 1.0,
            x + 1.0,
            y - 1.0,
            tags="all",
            outline="BLACK",
            fill="BLACK",
        )
    UsualHit = settings["IsHit"]

    settings = data["FuzzyMissile"]
    curvesFuzzy = np.hstack(tuple(map(requestPointToNPPoint, settings["Trajectory"])))
    FuzzyP = np.shape(curvesFuzzy)
    for i in range(FuzzyP[1] - 1):
        x = curvesFuzzy[0][i]
        y = curvesFuzzy[1][i]
        canvas.create_oval(
            x - 1.0, y + 1.0, x + 1.0, y - 1.0, tags="all", outline="RED", fill="RED"
        )
    FuzzyHit = settings["IsHit"]

    print("Попадание обычной ракетой:", UsualHit)
    print("Попадание fuzzy - ракетой:", FuzzyHit)

    if UsualHit:
        lbl_rock_1.config(text="Попадание обычной ракетой: да")
    else:
        lbl_rock_1.config(text="Попадание обычной ракетой: нет")

    if FuzzyHit:
        lbl_rock_2.config(text="Попадание fuzzy - ракетой: да")
    else:
        lbl_rock_2.config(text="Попадание fuzzy - ракетой: нет")

    oval1 = canvas.create_oval(
        0, 0, 0, 0, tags="all", outline="white", fill="dark orange"
    )
    oval2 = canvas.create_oval(0, 0, 0, 0, tags="all", outline="white", fill="gray50")
    oval3 = canvas.create_oval(
        0, 0, 0, 0, tags="all", outline="white", fill="indian red"
    )
    for i in range(res_points - 5):
        x1 = curvesBasicPoints[0][i]
        y1 = curvesBasicPoints[1][i]
        canvas.coords(oval1, x1 - 5.0, y1 + 5.0, x1 + 5.0, y1 - 5.0)
        time.sleep(0.02)
        window.update()

        if i < UsualP[1]:
            x2 = curvesUsual[0][i]
            y2 = curvesUsual[1][i]
            canvas.coords(oval2, x2 - 5.0, y2 + 5.0, x2 + 5.0, y2 - 5.0)
            window.update()

        if i < FuzzyP[1]:
            x3 = curvesFuzzy[0][i]
            y3 = curvesFuzzy[1][i]
            canvas.coords(oval3, x3 - 5.0, y3 + 5.0, x3 + 5.0, y3 - 5.0)
            window.update()
        if i == FuzzyP[1] or i == UsualP[1]:
            break


if __name__ == "__main__":
    window = Tk()
    window.title("Задача наведения")
    w, h = 1800, 900
    window.geometry("%dx%d+0+0" % (w, h))

    img1 = Image.open("icons/rocket.png").convert("RGBA")
    img1 = img1.resize((60, 60))
    eimg1 = ImageTk.PhotoImage(img1)

    img2 = Image.open("icons/air_fighter.png").convert("RGBA")
    img2 = img2.resize((60, 60))
    eimg2 = ImageTk.PhotoImage(img2)

    img3 = Image.open("icons/play.png").convert("RGBA")
    img3 = img3.resize((60, 60))
    eimg3 = ImageTk.PhotoImage(img3)

    img4 = Image.open("icons/eraser.png").convert("RGBA")
    img4 = img4.resize((60, 60))
    eimg4 = ImageTk.PhotoImage(img4)

    for c in range(6):
        window.columnconfigure(index=c, weight=1)
    for r in range(7):
        window.rowconfigure(index=r, weight=1)

    canvas = Canvas(borderwidth=1, bg="WHITE", cursor="pencil", width=1500, height=700)
    canvas.grid(row=0, column=1, columnspan=7, rowspan=4)

    btn1 = Button(text="button 2", image=eimg1, command=rocket)
    btn1.grid(row=0, column=0, ipadx=6, padx=5)

    btn2 = Button(text="button 3", image=eimg2, command=plane)
    btn2.grid(row=1, column=0, ipadx=6, padx=5)

    btn3 = Button(text="button 4", image=eimg3, command=start)
    btn3.grid(row=2, column=0, ipadx=6, ipady=6, padx=5)

    btn4 = Button(text="button 5", image=eimg4, command=erase)
    btn4.grid(row=3, column=0, ipadx=6, padx=5)

    lbl_points = Label(window, text="Количество точек маршрута:", font="RotondaC 14")
    lbl_points.grid(row=4, column=0)
    points = Entry(window, width=10)
    points.insert(0, "500")
    points.grid(row=5, column=0)

    lbl_velocity = Label(
        window, text="Скорость ракеты по умолчанию:", font="RotondaC 14"
    )
    lbl_velocity.grid(row=4, column=1)
    velocity = Entry(window, width=10)
    velocity.grid(row=5, column=1)
    velocity.insert(0, "7")

    lbl_coeff = Label(
        window,
        text="Коэффициент пропорциональности обычной ракеты:",
        font="RotondaC 14",
    )
    lbl_coeff.grid(row=4, column=2)
    coeff = Entry(window, width=10)
    coeff.grid(row=5, column=2)
    coeff.insert(0, "3")

    lbl_rock_1 = Label(
        text="Попадание обычной ракетой: {неизвестно, запустите симуляцию}",
        compound=RIGHT,
        font="RotondaC 14",
    )
    lbl_rock_1.grid(row=4, column=3)

    lbl_rock_2 = Label(
        text="Попадание fuzzy-ракетой: {неизвестно, запустите симуляцию}",
        compound=RIGHT,
        font="RotondaC 14",
    )
    lbl_rock_2.grid(row=5, column=3)

    window.mainloop()
