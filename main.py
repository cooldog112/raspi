import tkinter as tk
from PIL import Image, ImageTk
import cv2
import os
import time

# 전역 변수로 웹캠 객체 초기화
cap = None

# 웹캠 준비 함수
def initialize_camera():
    global cap
    cap = cv2.VideoCapture(1)  # USB 웹캠의 인덱스를 설정 (0은 기본 웹캠, 1은 USB 연결 웹캠)
    if not cap.isOpened():
        print("웹캠을 열 수 없습니다.")
        return False
    return True

# 프로그램 종료 시 웹캠 닫기
def close_camera():
    global cap
    if cap is not None:
        cap.release()

# 메인 화면을 보여주는 함수
def show_main_screen():
    # 기존에 표시된 모든 위젯을 제거
    for widget in root.winfo_children():
        widget.pack_forget()

    # 라디오 버튼 스타일 선택 화면 생성
    radio_frame = tk.Frame(root, bg='white')
    radio_frame.pack(fill="both", expand=True)

    # 제목 라벨 추가
    title_label = tk.Label(radio_frame, text="어떤 스타일로 찍을까요?", font=("Arial", 25, "bold"), fg="#FF69B4", bg='white')
    title_label.pack(pady=20)

    # 라디오 버튼 값 저장 변수 초기화
    radio_value = tk.StringVar(value="style1")

    # 스타일 이미지 파일 목록
    style_images = [
        "layout/cut1.png", "layout/cut2.png", "layout/cut3.png", "layout/cut4.png", "layout/cut5.png",
        "layout/cut6.png", "layout/cut7.png", "layout/cut8.png", "layout/cut9.png", "layout/cut10.png"
    ]

    # 버튼을 담을 프레임 생성
    buttons_frame = tk.Frame(radio_frame, bg='white')
    buttons_frame.pack()

    # 스타일 이미지와 라디오 버튼 생성
    for i, image_path in enumerate(style_images):
        img = Image.open(image_path)
        img = img.resize((160, 200), Image.Resampling.LANCZOS)
        img_tk = ImageTk.PhotoImage(img)

        if i % 5 == 0:
            row_frame = tk.Frame(buttons_frame, bg='white')
            row_frame.pack()

        radio_button = tk.Radiobutton(
            row_frame,
            text=f"",
            variable=radio_value,
            value=f"style{i+1}",
            font=("Arial", 18),
            bg='white',
            fg='black',
            selectcolor='pink',
            image=img_tk,
            compound="left"
        )
        radio_button.image = img_tk
        radio_button.pack(side="left", padx=10, pady=10)

    # 다음 버튼 생성
    next_button = tk.Button(radio_frame, text="선택 완료", font=("Arial", 20), command=lambda: start_camera(radio_value.get()))
    next_button.pack(pady=30)

    root.update()

# 카메라 화면을 시작하는 함수
def start_camera(selected_style):
    print(f"선택한 스타일은: {selected_style}")

    # 기존 위젯 제거
    for widget in root.winfo_children():
        widget.pack_forget()

    root.update_idletasks()

    # 카메라 캡처 시작
    cap = cv2.VideoCapture(1)

    # 카메라 화면 표시용 라벨 생성
    camera_label = tk.Label(root, width=800, height=600)
    camera_label.pack()

    # 저장 경로 설정
    save_path = "captured_photos"
    if not os.path.exists(save_path):
        os.makedirs(save_path)

    photo_count = 0
    max_photos = 6

    # 사진 개수와 카운트다운 표시용 라벨 생성
    photo_count_label = tk.Label(root, text=f"사진: {photo_count}/{max_photos}", font=("Arial", 18), bg="white")
    photo_count_label.pack(pady=10)

    countdown_label = tk.Label(root, text="", font=("Arial", 40, "bold"), fg="red", bg="white")
    countdown_label.pack(pady=20)

    def release_camera_and_next():
        """웹캠을 해제하고 다음 화면으로 전환."""
        cap.release()
        cv2.destroyAllWindows()
        show_photos_for_selection()

    # 사진 캡처 함수
    def capture_photo():
        nonlocal photo_count

        ret, frame = cap.read()
        if not ret:
            print("Failed to grab frame")
            return

        # 이미지를 저장
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        frame = cv2.flip(frame, 1)

        photo_filename = os.path.join(save_path, f"photo_{photo_count + 1}.png")
        cv2.imwrite(photo_filename, cv2.cvtColor(frame, cv2.COLOR_RGB2BGR))
        print(f"사진이 저장되었습니다: {photo_filename}")

        photo_count += 1
        photo_count_label.config(text=f"사진: {photo_count}/{max_photos}")

        if photo_count >= max_photos:
            release_camera_and_next()

    # 카운트다운 시작 함수
    def start_countdown():
        nonlocal photo_count

        if photo_count >= max_photos:
            return

        countdown = 2

        def update_countdown():
            nonlocal countdown

            if countdown > 0:
                countdown_label.config(text=str(countdown))
                countdown -= 1
                countdown_label.after(1000, update_countdown)
            else:
                countdown_label.config(text="")
                capture_photo()
                start_countdown()

        update_countdown()

    # 카메라 프레임 갱신 함수
    def update_frame():
        ret, frame = cap.read()
        if not ret:
            print("Failed to grab frame")
            return

        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        frame = cv2.flip(frame, 1)

        img = Image.fromarray(frame)
        img_tk = ImageTk.PhotoImage(image=img)

        camera_label.config(image=img_tk)
        camera_label.image = img_tk

        if photo_count < max_photos:
            camera_label.after(10, update_frame)

    update_frame()
    start_countdown()

def show_photos_for_selection():
    print("선택화면")

    # 기존 위젯 제거
    for widget in root.winfo_children():
        widget.pack_forget()

    photos = []
    save_path = "captured_photos"
    max_photos = 6

    # 저장된 사진 로드 및 리사이즈
    for i in range(max_photos):
        photo_filename = os.path.join(save_path, f"photo_{i + 1}.png")
        photo = Image.open(photo_filename)
        photo = photo.resize((200, 200), Image.Resampling.LANCZOS)
        photos.append(ImageTk.PhotoImage(photo))

    selected_count = 0

    # 선택된 사진 개수 표시 라벨 생성
    selected_count_label = tk.Label(root, text=f"선택된 사진: {selected_count}/4", font=("Arial", 18), bg="white")
    selected_count_label.pack(pady=10)

    checkbox_vars = [tk.BooleanVar() for _ in range(max_photos)]

    # 선택 상태 업데이트 함수
    def update_count():
        nonlocal selected_count
        selected_count = sum([var.get() for var in checkbox_vars])
        selected_count_label.config(text=f"선택된 사진: {selected_count}/4")
        if selected_count == 4:
            select_button.config(state="normal")
        else:
            select_button.config(state="disabled")

    # 사진과 체크박스 배치
    for i in range(0, max_photos, 2):
        row_frame = tk.Frame(root)
        row_frame.pack(pady=10)

        photo_label1 = tk.Label(row_frame, image=photos[i])
        photo_label1.image = photos[i]
        photo_label1.pack(side="left", padx=10)

        checkbox1 = tk.Checkbutton(row_frame, text=f"사진 {i + 1}", variable=checkbox_vars[i], font=("Arial", 15), command=update_count)
        checkbox1.pack(side="left", padx=10)

        if i + 1 < max_photos:
            photo_label2 = tk.Label(row_frame, image=photos[i + 1])
            photo_label2.image = photos[i + 1]
            photo_label2.pack(side="left", padx=10)

            checkbox2 = tk.Checkbutton(row_frame, text=f"사진 {i + 2}", variable=checkbox_vars[i + 1], font=("Arial", 15), command=update_count)
            checkbox2.pack(side="left", padx=10)

    # 선택 완료 버튼 생성
    select_button = tk.Button(root, text="선택 완료", font=("Arial", 20), command=lambda: print("사진 선택 완료"), state="disabled")
    select_button.pack(pady=20)


# GUI 초기화
root = tk.Tk()
root.title("매천네컷 프로그램")
root.geometry("1920x1080")

# 배경 이미지 설정
bg_image = Image.open("back.jpg")
bg_image = bg_image.resize((1920, 1080), Image.Resampling.LANCZOS)
bg_photo = ImageTk.PhotoImage(bg_image)

canvas = tk.Canvas(root, width=1920, height=1080)
canvas.pack(fill="both", expand=True)

canvas.create_image(0, 0, image=bg_photo, anchor="nw")

# 초기 화면 생성
main_screen = tk.Frame(root)
main_screen.place(relwidth=1, relheight=1)

# 초기 화면 제목과 시작 버튼 추가
title_label = tk.Label(main_screen, text="매천네컷", font=("Arial", 70, "bold"), bg="white")
title_label.pack(pady=50)

start_button = tk.Button(main_screen, text="인생네컷 시작하기", font=("Arial", 25), command=show_main_screen)
start_button.pack(pady=150)

# 웹캠 초기화
if not initialize_camera():
    print("프로그램을 종료합니다.")
    root.destroy()
else:
    print("웹캠이 준비되었습니다.")

# 프로그램 종료 시 웹캠 닫기
root.protocol("WM_DELETE_WINDOW", close_camera)

# GUI 루프 시작
root.mainloop()