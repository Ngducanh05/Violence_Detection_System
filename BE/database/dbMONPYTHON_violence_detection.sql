


-- ===============================
-- 1. USERS (người dùng hệ thống)
-- ===============================
CREATE TABLE IF NOT EXISTS users (
  user_id SERIAL PRIMARY KEY,
  name TEXT,
  email TEXT UNIQUE,
  password TEXT,       -- Thêm cột mật khẩu vào đây
  role TEXT DEFAULT 'annotator',
  created_at TIMESTAMP DEFAULT now()
);


-- ===============================
-- 2. PROJECTS (quản lý dự án)
-- ===============================
CREATE TABLE IF NOT EXISTS projects (
  project_id SERIAL PRIMARY KEY,
  name TEXT NOT NULL,
  description TEXT,
  created_at TIMESTAMP DEFAULT now(),
  owner_id INT REFERENCES users(user_id)
);

-- ===============================
-- 3. VIDEOS (video đầu vào)
-- ===============================
CREATE TABLE IF NOT EXISTS videos (
  video_id SERIAL PRIMARY KEY,
  project_id INT REFERENCES projects(project_id) ON DELETE SET NULL,
  filename TEXT NOT NULL,
  storage_path TEXT NOT NULL,
  duration_seconds FLOAT,
  fps FLOAT,
  width INT,
  height INT,
  source TEXT,
  uploaded_by INT REFERENCES users(user_id),
  uploaded_at TIMESTAMP DEFAULT now()
);
CREATE INDEX IF NOT EXISTS idx_videos_project ON videos(project_id);

-- ===============================
-- 4. SEGMENTS (đoạn video)
-- ===============================
CREATE TABLE IF NOT EXISTS segments (
  segment_id SERIAL PRIMARY KEY,
  video_id INT REFERENCES videos(video_id) ON DELETE CASCADE,
  start_time FLOAT NOT NULL,
  end_time FLOAT NOT NULL,
  label TEXT,
  created_by INT REFERENCES users(user_id),
  created_at TIMESTAMP DEFAULT now()
);
CREATE INDEX IF NOT EXISTS idx_segments_video ON segments(video_id);

-- ===============================
-- 5. ANNOTATIONS (frame-level)
-- ===============================
CREATE TABLE IF NOT EXISTS annotations (
  annotation_id SERIAL PRIMARY KEY,
  segment_id INT REFERENCES segments(segment_id) ON DELETE CASCADE,
  frame_index INT,
  bbox JSONB,
  class_name TEXT,
  confidence FLOAT,
  annotated_by INT REFERENCES users(user_id),
  created_at TIMESTAMP DEFAULT now()
);

-- ===============================
-- 6. MODELS (mô hình YOLO/CNN)
-- ===============================
CREATE TABLE IF NOT EXISTS models (
  model_id SERIAL PRIMARY KEY,
  name TEXT,
  version TEXT,
  description TEXT,
  path_to_weights TEXT,
  created_at TIMESTAMP DEFAULT now()
);

-- ===============================
-- 7. MODEL_RUNS (lịch sử huấn luyện / inference)
-- ===============================
CREATE TABLE IF NOT EXISTS model_runs (
  run_id SERIAL PRIMARY KEY,
  model_id INT REFERENCES models(model_id),
  project_id INT REFERENCES projects(project_id),
  started_at TIMESTAMP DEFAULT now(),
  finished_at TIMESTAMP,
  status TEXT,
  config JSONB
);
CREATE INDEX IF NOT EXISTS idx_model_runs_model ON model_runs(model_id);

-- ===============================
-- 8. RESULTS (kết quả dự đoán)
-- ===============================
CREATE TABLE IF NOT EXISTS results (
  result_id SERIAL PRIMARY KEY,
  run_id INT REFERENCES model_runs(run_id) ON DELETE SET NULL,
  video_id INT REFERENCES videos(video_id) ON DELETE CASCADE,
  segment_id INT REFERENCES segments(segment_id) ON DELETE SET NULL,
  detected_label TEXT,
  confidence FLOAT,
  frame_index INT,
  bbox JSONB,
  created_at TIMESTAMP DEFAULT now()
);
CREATE INDEX IF NOT EXISTS idx_results_video ON results(video_id);
CREATE INDEX IF NOT EXISTS idx_results_run ON results(run_id);

-- ===============================
-- 9. EVENTS (sự kiện bạo lực)
-- ===============================
CREATE TABLE IF NOT EXISTS events (
  event_id SERIAL PRIMARY KEY,
  video_id INT REFERENCES videos(video_id) ON DELETE CASCADE,
  segment_id INT REFERENCES segments(segment_id) ON DELETE SET NULL,
  detected_by_run INT REFERENCES model_runs(run_id) ON DELETE SET NULL,
  severity INT DEFAULT 1, -- 1=nhẹ, 2=vừa, 3=nặng
  description TEXT,
  created_at TIMESTAMP DEFAULT now()
);

-- ===============================
-- 10. AUDIT_LOGS (nhật ký hoạt động)
-- ===============================
CREATE TABLE IF NOT EXISTS audit_logs (
  log_id SERIAL PRIMARY KEY,
  user_id INT REFERENCES users(user_id),
  action TEXT,
  object_type TEXT,
  object_id INT,
  meta JSONB,
  created_at TIMESTAMP DEFAULT now()
);

-- ===============================
-- ✅ THÊM DỮ LIỆU MẪU (TÙY CHỌN)
-- ===============================
INSERT INTO users (name, email, role) VALUES
('Admin', 'admin@example.com', 'admin'),
('Annotator 1', 'annotator1@example.com', 'annotator');

INSERT INTO projects (name, description, owner_id) VALUES
('Violence Detection v1', 'Nhận diện hành vi bạo lực trong video camera', 1);

INSERT INTO videos (project_id, filename, storage_path, fps, width, height, source, uploaded_by)
VALUES (1, 'test_video.mp4', 'C:/data/test_video.mp4', 30, 1280, 720, 'local', 1);

INSERT INTO models (name, version, description, path_to_weights)
VALUES ('YOLOv8n', 'v1.0', 'Baseline YOLOv8 model', 'runs/train/violence_yolov8/weights/best.pt');
