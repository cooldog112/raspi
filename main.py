import tkinter as tk
from tkinter import messagebox
from PIL import Image, ImageTk
import cv2
from threading import Thread

def start_photobooth():
    # 인생네컷 시작하기 버튼 클릭 시 동작
    messagebox.showinfo("매천네컷", "인생네컷을 시작합니다!")
    # 모든 위젯 숨기기
    for widget in root.winfo_children():
        widget.place_forget()

    # 새로운 화면에 라디오 버튼 추가
    radio_frame = tk.Frame(root, bg="white")
    radio_frame.place(relx=0.5, rely=0.5, anchor="center")

    options = ["Option 1", "Option 2", "Option 3", "Option 4", "Option 5", "Option 6"]
    selected_option = tk.StringVar(value=options[0])

    tk.Label(radio_frame, text="옵션을 선택하세요:", font=("Helvetica", 14), bg="white").pack(pady=10)

    for option in options:
        tk.Radiobutton(
            radio_frame, text=option, variable=selected_option, value=option,
            font=("Helvetica", 12), bg="white"
        ).pack(anchor="w")

    tk.Button(radio_frame, text="확인", font=("Helvetica", 12), command=lambda: show_camera(radio_frame)).pack(pady=10)

def show_camera(frame_to_destroy):
    # 모든 기존 위젯 제거
    frame_to_destroy.destroy()

    # 카메라 출력 프레임 생성
    camera_frame = tk.Label(root)
    camera_frame.place(relx=0.5, rely=0.5, anchor="center")

    def update_frame():
        cap = cv2.VideoCapture(0)
        if not cap.isOpened():
            messagebox.showerror("Error", "카메라를 열 수 없습니다.")
            return

        while True:
            ret, frame = cap.read()
            if not ret:
                break

            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            frame = cv2.resize(frame, (400, 300))
            img = ImageTk.PhotoImage(image=Image.fromarray(frame))
            camera_frame.imgtk = img
            camera_frame.configure(image=img)

        cap.release()

    # 카메라 스레드 시작
    camera_thread = Thread(target=update_frame, daemon=True)
    camera_thread.start()

# 메인 윈도우 생성
root = tk.Tk()
root.title("매천네컷")
root.geometry("400x300")  # 창 크기 설정
root.resizable(False, False)  # 창 크기 조정 불가

# 배경 이미지 로드
try:
    background_image = Image.open("back.png")
    background_photo = ImageTk.PhotoImage(background_image.resize((400, 300)))
    background_label = tk.Label(root, image=background_photo)
    background_label.place(x=0, y=0, relwidth=1, relheight=1)
except Exception as e:
    print(f"Error loading background image: {e}")

# 타이틀 레이블
title_label = tk.Label(root, text="매천네컷", font=("Helvetica", 24, "bold"), pady=20, bg="white", fg="black")
title_label.place(relx=0.5, rely=0.3, anchor="center")

# 시작 버튼
start_button = tk.Button(root, text="인생네컷 시작하기", font=("Helvetica", 16), command=start_photobooth)
start_button.place(relx=0.5, rely=0.6, anchor="center")

# 이벤트 루프 시작
root.mainloop()
