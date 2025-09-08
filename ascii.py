import cv2
import numpy as np
from PIL import Image, ImageEnhance, ImageFilter
import time
import sys

VIDEO_PATH = "pacu.mp4"
WIDTH = 80
HEIGHT = 48
FPS = 10
MAX_DURATION = 15

ASCII_CHARS = " `'.,-~:;+=*!#%@█"

def auto_contrast(img):
    hist = img.histogram()
    min_gray = next(i for i, v in enumerate(hist) if v > 0)
    max_gray = next(i for i in reversed(range(256)) if hist[i] > 0)
    scale = 255 / (max_gray - min_gray + 1e-5)
    lut = [max(0, min(255, int((i - min_gray) * scale))) for i in range(256)]
    return img.point(lut)

def frame_to_ascii(frame):
    img = Image.fromarray(frame).convert("L")
    img = auto_contrast(img)
    img = ImageEnhance.Contrast(img).enhance(2.6)
    img = ImageEnhance.Brightness(img).enhance(1.15)
    edge = img.filter(ImageFilter.FIND_EDGES)
    sharp = img.filter(ImageFilter.SHARPEN)
    img = Image.blend(sharp, edge, 0.5)
    img = img.resize((WIDTH, HEIGHT))
    pixels = np.array(img)

    ascii_img = []
    for row in pixels:
        line = ''.join(ASCII_CHARS[int(p / 256 * len(ASCII_CHARS))] * 2 for p in row)
        ascii_img.append(line)
    return '\n'.join(ascii_img)

cap = cv2.VideoCapture(VIDEO_PATH)
if not cap.isOpened():
    print("❌ Video gagal dibuka! Cek nama file atau lokasi.")
    sys.exit()

video_fps = cap.get(cv2.CAP_PROP_FPS) or 25
interval = max(1, int(video_fps // FPS))
total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))

max_frames = total_frames
if MAX_DURATION:
    max_frames = min(total_frames, int(FPS * MAX_DURATION))

ascii_frames = []
count = 0
while cap.isOpened() and len(ascii_frames) < max_frames:
    ret, frame = cap.read()
    if not ret:
        break
    if count % interval == 0:
        ascii_frames.append(frame_to_ascii(frame))
    count += 1
cap.release()

print(f"✅ Total frame ASCII yang berhasil diambil: {len(ascii_frames)}")

if len(ascii_frames) == 0:
    print("⚠️ Tidak ada frame yang berhasil dikonversi.")
    sys.exit()

delay = 1 / FPS

try:
    while True:
        for f in ascii_frames:
            print("\033[H\033[J", end="")  # Bersihkan layar (compatible)
            print("\033[1;37mPACU JALUR ASCII MODE\033[0m\n")
            print("\033[1;37m" + f + "\033[0m")
            time.sleep(delay)
except KeyboardInterrupt:
    print("\n✅ Selesai.")
