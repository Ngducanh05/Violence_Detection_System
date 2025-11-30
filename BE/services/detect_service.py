import torch
import cv2
import numpy as np
from collections import deque
from ultralytics import YOLO
import tempfile
import hashlib
from models.classifier import ViolenceLSTM

from services.model_runs_service import create_model_run, finish_model_run
from services.results_service import create_result
from services.segments_service import create_segment
from services.events_service import create_event
from schemas.model_runs import ModelRunCreate


DEVICE = "cuda" if torch.cuda.is_available() else "cpu"
T = 32
THRESHOLD = 0.30

# ============================
# LOAD MODELS (NO .half() HERE)
# ============================
bbox_model = YOLO("weights/yolov8x.pt").to(DEVICE)
pose_model = YOLO("weights/yolov8l-pose.pt").to(DEVICE)

lstm_model = ViolenceLSTM(34, 128, 2).to(DEVICE)
lstm_model.load_state_dict(torch.load("weights/best_pose_model.pth", map_location=DEVICE))
lstm_model.eval()   # giữ float32 để tránh lỗi LSTM fp16


def hash_bytes(b):
    return hashlib.sha256(b).hexdigest()


# ======================================================================
# MAIN PIPELINE
# ======================================================================
async def run_violence_pipeline(db, file, project_id, user_id):
    contents = await file.read()
    video_hash = hash_bytes(contents)

    temp = tempfile.NamedTemporaryFile(delete=False, suffix=".mp4")
    temp.write(contents)
    temp.close()

    cap = cv2.VideoCapture(temp.name)
    fps = cap.get(cv2.CAP_PROP_FPS) or 30

    frame_interval = int(fps // 15) if fps >= 20 else 1
    buffer = deque(maxlen=T)

    frames_batch = []
    batch_indices = []
    batch_size = 16

    timeline = []
    segments = []
    events = []

    # ========== CREATE RUN ==========
    run = create_model_run(
        db,
        ModelRunCreate(
            model_id=1,
            project_id=project_id,
            config={"source": "violence-detection"},
        ),
    )
    run_id = run.run_id

    frame_idx = 0
    violent_frames = []

    # ==================================================================
    # PROCESS VIDEO
    # ==================================================================
    while True:
        ret, frame = cap.read()
        if not ret:
            break

        if frame_idx % frame_interval != 0:
            frame_idx += 1
            continue

        # Không chuyển float16 — YOLO xử lý uint8 OK
        frames_batch.append(frame)
        batch_indices.append(frame_idx)

        if len(frames_batch) == batch_size:
            out = process_batch(frames_batch, batch_indices, buffer, fps)
            timeline += out
            frames_batch.clear()
            batch_indices.clear()

        frame_idx += 1

    # last batch
    if len(frames_batch) > 0:
        out = process_batch(frames_batch, batch_indices, buffer, fps)
        timeline += out

    cap.release()

    # ==================================================================
    # SAVE RESULTS
    # ==================================================================
    for item in timeline:
        create_result(
            db,
            {
                "run_id": run_id,
                "video_id": None,
                "segment_id": None,
                "frame_index": item["frame"],
                "detected_label": "violent" if item["score"] >= THRESHOLD else "non-violent",
                "confidence": item["score"],
                "bbox": None,
            },
        )

        if item["score"] >= THRESHOLD:
            violent_frames.append(item["frame"])

    # ==================================================================
    # SEGMENTS
    # ==================================================================
    segments = extract_segments(violent_frames, fps)
    for seg in segments:
        rec = create_segment(
            db,
            {
                "project_id": project_id,
                "video_id": None,
                "start_time": seg["start"],
                "end_time": seg["end"],
            },
            created_by=user_id
        )
        seg["id"] = rec.segment_id

    # ==================================================================
    # EVENTS
    # ==================================================================
    # ==================================================================
# EVENTS
# ==================================================================
    for seg in segments:
        ev = create_event(
            db,
            {
                "project_id": project_id,
                "video_id": None,
                "segment_id": seg["id"],
                "detected_by_run": run_id,
                "event_type": "violence",
                "score": seg["score"],
                "timestamp": seg["start"],
            },
            created_by=user_id   # <<< BẮT BUỘC
        )

        events.append({
            "id": ev.event_id,
            "time": seg["start"],
            "score": seg["score"],
        })


    # ==================================================================
    # FINISH RUN
    # ==================================================================
    finish_model_run(db, run_id)

    return {
        "run_id": run_id,
        "timeline": timeline,
        "segments": segments,
        "events": events,
    }


# ======================================================================
# PROCESS BATCH — SAFE FP32
# ======================================================================
def process_batch(frames, indices, buffer, fps):
    timeline = []

    # YOLO tự quản half=True nếu GPU hoạt động tốt
    dets = bbox_model(frames, device=DEVICE, half=(DEVICE == "cuda"))

    for i, det in enumerate(dets):
        frame = frames[i]
        frame_idx = indices[i]

        if len(det.boxes) == 0:
            continue

        boxes = det.boxes.xyxy.cpu().numpy()
        x1, y1, x2, y2 = boxes[np.argmax((boxes[:, 2]-boxes[:, 0]) * (boxes[:, 3]-boxes[:, 1]))].astype(int)

        crop = frame[y1:y2, x1:x2]
        if crop.size == 0:
            continue

        crop = cv2.resize(crop, (320, 320))
        pose = pose_model(crop, device=DEVICE, half=(DEVICE == "cuda"), verbose=False)

        if len(pose[0].keypoints) == 0:
            continue

        kp = pose[0].keypoints[0]
        pts = kp.xy.cpu().numpy()
        conf = kp.conf.cpu().numpy()

        if conf.mean() < 0.5:
            continue

        pts = pts[0] if pts.ndim == 3 else pts
        pts_norm = (pts / 320.0).flatten()

        buffer.append(pts_norm)

        if len(buffer) == T:
            arr = np.stack(buffer).astype(np.float32)
            tensor = torch.tensor(arr, dtype=torch.float32, device=DEVICE).unsqueeze(0)

            with torch.no_grad():
                logits = lstm_model(tensor)
                prob = torch.softmax(logits, dim=1)[0][1].item()

            timeline.append({
                "frame": frame_idx,
                "time": round(frame_idx / fps, 3),
                "score": round(prob, 4),
            })

    return timeline


# ======================================================================
# SEGMENT BUILDER
# ======================================================================
def extract_segments(frames, fps):
    if not frames:
        return []

    segments = []
    start = frames[0]
    prev = start

    for f in frames[1:]:
        if f - prev > fps * 2:
            segments.append({
                "start": round(start / fps, 2),
                "end": round(prev / fps, 2),
                "score": 1.0,
            })
            start = f
        prev = f

    segments.append({
        "start": round(start / fps, 2),
        "end": round(prev / fps, 2),
        "score": 1.0,
    })

    return segments
