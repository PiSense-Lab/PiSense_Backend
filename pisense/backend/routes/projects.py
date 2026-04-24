from fastapi import APIRouter
from pisense.backend.classes import Database


router = APIRouter(prefix="/projects")

@router.get("/get_project")
async def get_project(project_id: int, name: str | None = None):
    """
    Retrieve a single project record.

    params:
        project_id: ID of the project to retrieve.
        name: Optional project name to filter by.

    returns:
        A project dictionary with id, name, description, public, archived, and owner_id.
    """
    db = Database()
    res = db.get_project(project_id, name=name)
    return {
        "id": res.id,
        "name": res.name,
        "description": res.description,
        "public": res.public,
        "archived": res.archived,
        "owner_id": res.owner_id,
    }


@router.post("/create_project", status_code=201)
async def create_project(
    name: str,
    owner_id: int,
    description: str = "",
    public: bool = False,
    archived: bool = False,
):
    """
    Create a new project.

    params:
        name: Name of the new project.
        owner_id: User ID that owns the project.
        description: Optional description of the project.
        public: Whether the project is public.
        archived: Whether the project is archived.

    returns:
        The created project record.
    """
    db = Database()
    project = db.create_project(
        name=name,
        owner_id=owner_id,
        description=description,
        public=public,
        archived=archived
    )
    return {
        "id": project.id,
        "name": project.name,
        "description": project.description,
        "public": project.public,
        "archived": project.archived,
        "owner_id": project.owner_id,
        "last_updated": project.last_updated,
    }
