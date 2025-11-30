import torch
import cv2
import numpy as np
from collections import deque
from ultralytics import YOLO
import tempfile
from models.classifier import ViolenceLSTM

# ==============================
# GPU CONFIG
# ==============================
DEVICE = "cuda" if torch.cuda.is_available() else "cpu"
T = 32
THRESHOLD = 0.30

print(f"🚀 Using device: {DEVICE}")

# ==============================
# LOAD MODELS TO GPU
# ==============================
bbox_model = YOLO("weights/yolov8x.pt")
pose_model = YOLO("weights/yolov8l-pose.pt")

bbox_model.to(DEVICE)
pose_model.to(DEVICE)

lstm_model = ViolenceLSTM(
    input_size=34,
    hidden_size=128,
    num_layers=2
).to(DEVICE)

state = torch.load("weights/best_pose_model.pth", map_location=DEVICE)
lstm_model.load_state_dict(state)
lstm_model.eval()

bbox_model.to(DEVICE).half()
pose_model.to(DEVICE).half()
lstm_model.half()


# ==============================
# VIDEO PROCESSING
# ==============================
# Update chức năng xử lý video để trả về timeline với điểm số theo thời gian
async def process_video(file):
    contents = await file.read()

    # Tạo file tạm
    temp = tempfile.NamedTemporaryFile(delete=False, suffix=".mp4")
    temp.write(contents)
    temp.close()

    cap = cv2.VideoCapture(temp.name)
    fps = cap.get(cv2.CAP_PROP_FPS) or 30
    buffer = deque(maxlen=T)

    timeline = []  # ← NEW: lưu toàn bộ kết quả theo frame
    frame_idx = 0

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        det = bbox_model(frame, verbose=False, device=DEVICE)
        if len(det[0].boxes) == 0:
            frame_idx += 1
            continue

        boxes = det[0].boxes.xyxy.cpu().numpy()
        areas = (boxes[:, 2] - boxes[:, 0]) * (boxes[:, 3] - boxes[:, 1])
        x1, y1, x2, y2 = boxes[np.argmax(areas)].astype(int)

        person = frame[y1:y2, x1:x2]
        if person.size == 0:
            frame_idx += 1
            continue

        crop = cv2.resize(person, (320, 320))

        pose_res = pose_model(crop, verbose=False, device=DEVICE)
        if len(pose_res[0].keypoints) == 0:
            frame_idx += 1
            continue

        kp = pose_res[0].keypoints[0]
        pts = kp.xy.cpu().numpy()
        conf = kp.conf.cpu().numpy()

        if pts.ndim == 3:
            pts = pts[0]
        if conf.ndim == 2:
            conf = conf[0]

        if conf.mean() < 0.5:
            frame_idx += 1
            continue

        pts_norm = (pts / 320.0).flatten()
        buffer.append(pts_norm)

        # Chỉ chạy LSTM khi đủ 32 frame
        if len(buffer) == T:
            seq_np = np.stack(buffer)
            seq_tensor = torch.tensor(seq_np, dtype=torch.float32, device=DEVICE).unsqueeze(0)

            with torch.no_grad():
                logits = lstm_model(seq_tensor)
                prob = torch.softmax(logits, dim=1)[0][1].item()

            timestamp = frame_idx / fps
            timeline.append({
                "frame": frame_idx,
                "time": round(timestamp, 3),
                "score": round(prob, 4)
            })

        frame_idx += 1

    cap.release()
    return timeline

