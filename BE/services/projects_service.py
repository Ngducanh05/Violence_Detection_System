from sqlalchemy.orm import Session
from models.db_models import Projects
from schemas.projects import ProjectCreate, ProjectUpdate


# Trả về project của đúng user
def get_all_projects(db: Session, owner_id: int):
    return db.query(Projects).filter(Projects.owner_id == owner_id).all()


def get_project_by_id(db: Session, project_id: int):
    return db.query(Projects).filter(Projects.project_id == project_id).first()


# CREATE PROJECT – owner_id = user_id đang login
def create_project(db: Session, data: ProjectCreate, owner_id: int):
    project = Projects(
        name=data.name,
        description=data.description,
        owner_id=owner_id
    )
    db.add(project)
    db.commit()
    db.refresh(project)
    return project


def update_project(db: Session, project_id: int, data: ProjectUpdate):
    project = get_project_by_id(db, project_id)
    if not project:
        return None

    if data.name is not None:
        project.name = data.name

    if data.description is not None:
        project.description = data.description

    db.commit()
    db.refresh(project)
    return project


def delete_project(db: Session, project_id: int):
    project = get_project_by_id(db, project_id)
    if not project:
        return False

    db.delete(project)
    db.commit()
    return True
