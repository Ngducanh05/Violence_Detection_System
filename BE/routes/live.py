from fastapi import APIRouter, WebSocket, WebSocketDisconnect
import cv2
import numpy as np
import base64
import torch
from models.model_loader import bbox_model, pose_model, lstm_model, DEVICE, T
from collections import deque

router = APIRouter(prefix="/live", tags=["Live Detection"])

buffer = deque(maxlen=T)


def preprocess_frame(base64_data):
    if "," in base64_data:
        base64_data = base64_data.split(",")[1]
    img_bytes = base64.b64decode(base64_data)
    np_arr = np.frombuffer(img_bytes, np.uint8)
    return cv2.imdecode(np_arr, cv2.IMREAD_COLOR)


@router.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()

    try:
        while True:
            # 1. Nhận frame từ FE
            data = await websocket.receive_text()
            frame = preprocess_frame(data)
            if frame is None:
                continue

            # 2. YOLO detect → lấy bbox người lớn nhất
            det = bbox_model(frame, verbose=False, device=DEVICE)
            if len(det[0].boxes) == 0:
                await websocket.send_json({"label": "no person", "score": 0})
                continue

            boxes = det[0].boxes.xyxy.cpu().numpy()
            areas = (boxes[:, 2] - boxes[:, 0]) * (boxes[:, 3] - boxes[:, 1])
            x1, y1, x2, y2 = boxes[np.argmax(areas)].astype(int)

            crop = frame[y1:y2, x1:x2]
            if crop.size == 0:
                await websocket.send_json({"label": "error", "score": 0})
                continue

            crop_resized = cv2.resize(crop, (320, 320))

            # 3. YOLO pose
            pose_res = pose_model(crop_resized, verbose=False, device=DEVICE)
            if len(pose_res[0].keypoints) == 0:
                await websocket.send_json({"label": "no pose", "score": 0})
                continue

            kp = pose_res[0].keypoints[0]
            pts = kp.xy.cpu().numpy()
            conf = kp.conf.cpu().numpy()

            if pts.ndim == 3: pts = pts[0]
            if conf.ndim == 2: conf = conf[0]
            if conf.mean() < 0.5:
                await websocket.send_json({"label": "low pose", "score": 0})
                continue

            pts_norm = (pts / 320.0).flatten()
            buffer.append(pts_norm)

            # 4. Chạy LSTM nếu đủ 32 frame
            score = 0
            label = "non-violent"

            if len(buffer) == T:
                seq_np = np.stack(buffer)
                seq_tensor = torch.tensor(
                    seq_np, dtype=torch.float32, device=DEVICE
                ).unsqueeze(0)

                with torch.no_grad():
                    logits = lstm_model(seq_tensor)
                    p_non, p_viol = torch.softmax(logits, dim=1)[0].tolist()
                    score = round(float(p_viol), 4)
                    label = "violent" if score >= 0.30 else "non-violent"

            # 5. Vẽ bbox + label lên frame preview
            cv2.rectangle(frame, (x1, y1), (x2, y2), (0,255,0) if label=="non-violent" else (0,0,255), 2)
            cv2.putText(frame, f"{label.upper()} {score:.2f}", (x1, y1-10),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.8,
                        (0,255,0) if label=="non-violent" else (0,0,255), 2)

            # 6. Encode để gửi FE hiển thị
            _, buffer_img = cv2.imencode(".jpg", frame)
            encoded = base64.b64encode(buffer_img).decode("utf-8")

            await websocket.send_json({
                "label": label,
                "score": score,
                "bbox": [int(x1), int(y1), int(x2), int(y2)],
                "image": f"data:image/jpeg;base64,{encoded}"
            })

    except WebSocketDisconnect:
        print("WS disconnected")

    except Exception as e:
        print("WS error:", e)
