from sqlalchemy import Column, Integer, String, Float, Text, ForeignKey, JSON, TIMESTAMP
from sqlalchemy.orm import declarative_base, relationship
from datetime import datetime

Base = declarative_base()


# ===============================
# 1. USERS
# ===============================
class Users(Base):
    __tablename__ = "users"

    user_id = Column(Integer, primary_key=True, index=True)
    name = Column(Text)
    email = Column(Text, unique=True, index=True)
    password = Column(Text)
    role = Column(Text, default="annotator")
    created_at = Column(TIMESTAMP, default=datetime.utcnow)


# ===============================
# 2. PROJECTS
# ===============================
class Projects(Base):
    __tablename__ = "projects"

    project_id = Column(Integer, primary_key=True)
    name = Column(Text, nullable=False)
    description = Column(Text)
    created_at = Column(TIMESTAMP, default=datetime.utcnow)
    owner_id = Column(Integer, ForeignKey("users.user_id"))

    owner = relationship("Users")


# ===============================
# 3. VIDEOS
# ===============================
class Videos(Base):
    __tablename__ = "videos"

    video_id = Column(Integer, primary_key=True)
    project_id = Column(Integer, ForeignKey("projects.project_id"))
    filename = Column(Text, nullable=False)
    storage_path = Column(Text, nullable=False)
    duration_seconds = Column(Float)
    fps = Column(Float)
    width = Column(Integer)
    height = Column(Integer)
    source = Column(Text)
    uploaded_by = Column(Integer, ForeignKey("users.user_id"))
    uploaded_at = Column(TIMESTAMP, default=datetime.utcnow)

    project = relationship("Projects")
    uploader = relationship("Users")


# ===============================
# 4. SEGMENTS
# ===============================
class Segments(Base):
    __tablename__ = "segments"

    segment_id = Column(Integer, primary_key=True)
    video_id = Column(Integer, ForeignKey("videos.video_id"))
    start_time = Column(Float, nullable=False)
    end_time = Column(Float, nullable=False)
    label = Column(Text)
    created_by = Column(Integer, ForeignKey("users.user_id"))
    created_at = Column(TIMESTAMP, default=datetime.utcnow)

    video = relationship("Videos")
    creator = relationship("Users")


# ===============================
# 5. ANNOTATIONS
# ===============================
class Annotations(Base):
    __tablename__ = "annotations"

    annotation_id = Column(Integer, primary_key=True)
    segment_id = Column(Integer, ForeignKey("segments.segment_id"))
    frame_index = Column(Integer)
    bbox = Column(JSON)
    class_name = Column(Text)
    confidence = Column(Float)
    annotated_by = Column(Integer, ForeignKey("users.user_id"))
    created_at = Column(TIMESTAMP, default=datetime.utcnow)

    segment = relationship("Segments")
    annotator = relationship("Users")


# ===============================
# 6. MODELS
# ===============================
class Models(Base):
    __tablename__ = "models"

    model_id = Column(Integer, primary_key=True)
    name = Column(Text)
    version = Column(Text)
    description = Column(Text)
    path_to_weights = Column(Text)
    created_at = Column(TIMESTAMP, default=datetime.utcnow)


# ===============================
# 7. MODEL_RUNS
# ===============================
class ModelRuns(Base):
    __tablename__ = "model_runs"

    run_id = Column(Integer, primary_key=True)
    model_id = Column(Integer, ForeignKey("models.model_id"))
    project_id = Column(Integer, ForeignKey("projects.project_id"))
    started_at = Column(TIMESTAMP, default=datetime.utcnow)
    finished_at = Column(TIMESTAMP)
    status = Column(Text)
    config = Column(JSON)

    model = relationship("Models")
    project = relationship("Projects")


# ===============================
# 8. RESULTS
# ===============================
class Results(Base):
    __tablename__ = "results"

    result_id = Column(Integer, primary_key=True)
    run_id = Column(Integer, ForeignKey("model_runs.run_id"))
    video_id = Column(Integer, ForeignKey("videos.video_id"))
    segment_id = Column(Integer, ForeignKey("segments.segment_id"))
    detected_label = Column(Text)
    confidence = Column(Float)
    frame_index = Column(Integer)
    bbox = Column(JSON)
    created_at = Column(TIMESTAMP, default=datetime.utcnow)

    run = relationship("ModelRuns")
    video = relationship("Videos")
    segment = relationship("Segments")


# ===============================
# 9. EVENTS
# ===============================
class Events(Base):
    __tablename__ = "events"

    event_id = Column(Integer, primary_key=True)
    video_id = Column(Integer, ForeignKey("videos.video_id"))
    segment_id = Column(Integer, ForeignKey("segments.segment_id"))
    detected_by_run = Column(Integer, ForeignKey("model_runs.run_id"))
    severity = Column(Integer, default=1)
    description = Column(Text)
    created_at = Column(TIMESTAMP, default=datetime.utcnow)
    created_by = Column(Integer, nullable=True)

    video = relationship("Videos")
    segment = relationship("Segments")
    run = relationship("ModelRuns")


# ===============================
# 10. AUDIT_LOGS
# ===============================
class AuditLogs(Base):
    __tablename__ = "audit_logs"

    log_id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.user_id"))
    action = Column(Text)
    object_type = Column(Text)
    object_id = Column(Integer)
    meta = Column(JSON)
    created_at = Column(TIMESTAMP, default=datetime.utcnow)

    user = relationship("Users")
