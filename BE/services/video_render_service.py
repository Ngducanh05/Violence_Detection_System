import cv2
import os

def render_video_with_overlay(input_path, output_path, timeline):
    cap = cv2.VideoCapture(input_path)
    fps = cap.get(cv2.CAP_PROP_FPS) or 30
    w = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    h = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    writer = cv2.VideoWriter(output_path, fourcc, fps, (w, h))

    frame_map = {t["frame"]: t for t in timeline}
    frame_idx = 0

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        item = frame_map.get(frame_idx)
        if item:
            score = item["score"]
            label = "violent" if score >= 0.30 else "non-violent"
            color = (0, 0, 255) if label == "violent" else (0, 255, 0)

            cv2.putText(frame, f"{label.upper()} {score:.2f}",
                        (20, 40), cv2.FONT_HERSHEY_SIMPLEX, 1, color, 2)

        writer.write(frame)
        frame_idx += 1

    cap.release()
    writer.release()
