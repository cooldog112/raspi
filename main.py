import tkinter as tk
from PIL import Image, ImageTk
import cv2
import os
import time

# 전역 변수로 웹캠 객체 초기화
cap = None
select_style = ""
select_photo = []
# 웹캠 준비 함수
def initialize_camera():
    global cap
    cap = cv2.VideoCapture(0)  # USB 웹캠의 인덱스를 설정 (0은 기본 웹캠, 1은 USB 연결 웹캠)
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
    global select_style
    # 기존에 표시된 모든 위젯을 제거
    for widget in root.winfo_children():
        print(f"Hiding widget: {widget.winfo_name()} (Type: {type(widget).__name__})")
        widget.pack_forget()
        widget.place_forget()

    # 라디오 버튼 스타일 선택 화면 생성
    radio_frame = tk.Frame(root)
    radio_frame.pack(fill="both", expand=True)

    # 제목 라벨 추가
    style_title = tk.Label(radio_frame, text="어떤 스타일로 찍을까요?", font=("Arial", 25, "bold"), fg="#FF69B4")
    style_title.pack(pady=20)

    # 라디오 버튼 값 저장 변수 초기화
    radio_value = tk.StringVar(value="style1")

    # 스타일 이미지 파일 목록
    style_images = [
        "layout/style1.png", "layout/style2.png", "layout/style3.png", "layout/style4.png", "layout/style5.png",
        "layout/style6.png", "layout/style7.png", "layout/style8.png", "layout/style9.png", "layout/style10.png"
    ]

    # 버튼을 담을 프레임 생성
    buttons_frame = tk.Frame(radio_frame)
    buttons_frame.pack()

    # 스타일 이미지와 라디오 버튼 생성
    for i, image_path in enumerate(style_images):
        img = Image.open(image_path)
        img = img.resize((int(320*0.8), int(480*0.8)), Image.Resampling.LANCZOS)
        img_tk = ImageTk.PhotoImage(img)

        if i % 5 == 0:
            row_frame = tk.Frame(buttons_frame,)
            row_frame.pack()

        radio_button = tk.Radiobutton(
            row_frame,
            text=f"",
            variable=radio_value,
            value=f"style{i+1}",
            font=("Arial", 40),            
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
    global select_style
    select_style = selected_style
    # 기존 위젯 제거
    for widget in root.winfo_children():
        widget.pack_forget()
        widget.place_forget()

    root.update_idletasks()

    # 카메라 캡처 시작
    cap = cv2.VideoCapture(0)
    print("TEST")
    # 카메라 화면 표시용 라벨 생성
    camera_label = tk.Label(root, width=640, height=960)
    camera_label.pack()

    # 저장 경로 설정
    save_path = "captured_photos"
    if not os.path.exists(save_path):
        os.makedirs(save_path)

    photo_count = 0
    max_photos = 6

    # 사진 개수와 카운트다운 표시용 라벨 생성
    photo_count_label = tk.Label(root, text=f"사진: {photo_count}/{max_photos}", font=("Arial", 18))
    photo_count_label.pack(pady=10)

    countdown_label = tk.Label(root, text="", font=("Arial", 200, "bold"), fg="red")
    countdown_label.place(relx=0.2, rely=0.5, anchor="center")

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
        x, y, w, h = 160,0,320,420
        frame = frame[y:y+h, x:x+w]


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

        x, y, w, h = 160,0,320,420
        cropped_frame = frame[y:y+h, x:x+w]

        img = Image.fromarray(cropped_frame)  
        img = img.resize((int(320*2), int(420*2)), Image.Resampling.LANCZOS)      
        img_tk = ImageTk.PhotoImage(image=img)

        camera_label.config(image=img_tk)
        camera_label.image = img_tk

        if photo_count < max_photos:
            camera_label.after(10, update_frame)

    update_frame()
    start_countdown()

def show_photos_for_selection():
    global select_photo
    for widget in root.winfo_children():
        widget.pack_forget()
        widget.place_forget()

    photos = []
    save_path = "captured_photos"
    max_photos = 6

    # 저장된 사진 로드 및 리사이즈
    for i in range(max_photos):
        photo_filename = os.path.join(save_path, f"photo_{i + 1}.png")
        photo = Image.open(photo_filename)
        photo = photo.resize((int(320 * 0.8), int(420 * 0.8)), Image.Resampling.LANCZOS)
        photos.append(ImageTk.PhotoImage(photo))

    selected_count = 0

    # 선택된 사진 개수 표시 라벨 생성
    selected_count_label = tk.Label(root, text=f"선택된 사진: {selected_count}/4", font=("Arial", 18), bg="white")
    selected_count_label.pack(pady=10)

    checkbox_vars = [tk.BooleanVar() for _ in range(max_photos)]

    # 선택 상태 업데이트 함수
    def update_count():
        nonlocal selected_count
        select_photo.clear()
        selected_count = sum([var.get() for var in checkbox_vars])
        selected_count_label.config(text=f"선택된 사진: {selected_count}/4")
        
        # 선택된 사진의 인덱스 저장
        for idx, var in enumerate(checkbox_vars):
            if var.get():
                select_photo.append(idx + 1)

        # 선택 완료 버튼 활성화/비활성화
        if selected_count == 4:
            select_button.config(state="normal")
        else:
            select_button.config(state="disabled")

    # 사진과 체크박스 배치 (2행 3열)
    for i in range(0, max_photos, 3):
        row_frame = tk.Frame(root)
        row_frame.pack(pady=10)

        for j in range(3):
            if i + j < max_photos:
                checkbox = tk.Checkbutton(
                    row_frame,
                    text=f"{i + j + 1}",
                    variable=checkbox_vars[i + j],
                    font=("Arial", 20),
                    image=photos[i + j],  # 이미지 설정
                    compound="top",  # 이미지를 텍스트 위에 배치
                    command=update_count
                )
                checkbox.image = photos[i + j]  # 참조 유지
                checkbox.pack(side="left", padx=10)

    select_button = tk.Button(root, text="선택 완료", font=("Arial", 20), command=show_photo, state="disabled")
    select_button.pack(pady=20)


from PIL import Image, ImageTk

def show_photo():    
    print(select_photo)
    for widget in root.winfo_children():
        widget.pack_forget()
        widget.place_forget()

    show_photo_title = tk.Label(root, text="사진확인하기", font=("Arial", 25, "bold"), fg="#FF69B4")
    show_photo_title.pack(pady=20)

    save_path = "captured_photos"
    max_photos = 4

    photos = []
    photo = Image.open("layout/"+select_style+".png")
    photo = photo.resize((640, 960), Image.Resampling.LANCZOS)
    photos.append(photo)
    # 저장된 사진 로드 및 리사이즈
    for i in select_photo:
        photo_filename = os.path.join(save_path, f"photo_{i}.png")
        if os.path.exists(photo_filename):
            photo = Image.open(photo_filename).convert("RGBA")  # RGBA로 변환
            photo = photo.resize((320, 420), Image.Resampling.LANCZOS)  # 작은 사진들
            photos.append(photo)

    # 메인 사진 표시
    if photos:
        # 배경을 생성
        base_image = photos[0].copy()

        # 작은 사진들을 메인 사진 위에 겹치기
        positions = [(0, 0), (0, 420), (320, 0), (320, 420)]  # 작은 사진 위치

        for idx, (x, y) in enumerate(positions):
            if idx + 1 < len(photos):
                overlay_image = photos[idx + 1]
                base_image.paste(overlay_image, (x, y), overlay_image)  # 알파 채널 유지
        base_image.paste(photos[0], (0, 0), photos[0])

        # 최종 이미지를 tkinter에서 사용 가능한 형식으로 변환
        final_image = ImageTk.PhotoImage(base_image)

        # 최종 이미지를 표시
        main_photo_label = tk.Label(root, image=final_image)
        main_photo_label.image = final_image
        main_photo_label.pack(pady=20)

    else:
        error_label = tk.Label(root, text="사진 파일이 존재하지 않습니다.", font=("Arial", 18), fg="red")
        error_label.pack(pady=20)



# GUI 초기화
root = tk.Tk()
root.title("매천네컷 프로그램")
root.geometry("1920x1080")


# 배경 이미지 설정
try:
    bg_image = Image.open("background.png")
    bg_image = bg_image.resize((1920, 1080), Image.Resampling.LANCZOS)
    bg_photo = ImageTk.PhotoImage(bg_image)
except Exception as e:
    print(f"Error loading image: {e}")
    exit()

canvas = tk.Label(root, image=bg_photo)
canvas.image = bg_photo  # 참조를 유지
canvas.pack(fill="both", expand=True)


# "시작하기" 버튼 이미지 설정
try:
    btn_image = Image.open("start_btn.png")    
    btn_photo = ImageTk.PhotoImage(btn_image)
except Exception as e:
    print(f"Error loading button image: {e}")
    exit()

start_button = tk.Button(root, image=btn_photo, command=show_main_screen, borderwidth=0)  # 테두리 제거
start_button.image = btn_photo  # 참조 유지
start_button.place(relx=0.5, rely=0.8, anchor="center")  # 가운데 정렬

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