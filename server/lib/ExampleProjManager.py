import base64
import io
import json
from datetime import datetime, timezone

from loguru import logger
from pydantic import BaseModel

from server.config import EXAMPLE_USER_EMAIL, EXAMPLE_USER_USERNAME, EXAMPLES_DIR
from server.lib.FileManager import FileManager
from server.lib.utils import get_project_by_id_sync
from server.models.database import (
    DatabaseTransaction,
    FileRecord,
    NodeOutputRecord,
    ProjectRecord,
    SessionLocal,
    UserRecord,
)
from server.models.project import ProjUIState, ProjWorkflow


class ExampleFile(BaseModel):
    key: str
    filename: str
    format: str
    node_id: str
    file_size: int
    content: str  # base64 encoded content


class ExampleData(BaseModel):
    old_id: int
    node_id: str
    port: str
    data: str  # base64 encoded pickled data


class ExampleProject(BaseModel):
    """
    A self-contained project package including metadata, workflow, files, and data.
    """

    project_name: str
    updated_at: int
    thumb: str | None
    editable: bool
    workflow: ProjWorkflow
    ui_state: ProjUIState

    files: list[ExampleFile]
    datas: list[ExampleData]


def initialize_example_projects() -> None:
    """
    Initialize example projects for the official learning user.
    """
    if not EXAMPLES_DIR.exists():
        return

    with DatabaseTransaction() as db:
        # 1. Ensure official user exists
        user = db.query(UserRecord).filter_by(username=EXAMPLE_USER_USERNAME).first()
        if not user:
            logger.info(f"Creating official learning user: {EXAMPLE_USER_USERNAME}")
            user = UserRecord(
                username=EXAMPLE_USER_USERNAME,
                email=EXAMPLE_USER_EMAIL,
                hashed_password=None,
                file_total_space=10 * 1024 * 1024 * 1024 * 1024, # 10 TB
            )
            db.add(user)
            db.flush()

        file_manager = FileManager(sync_db_session=db)
        
        # 2. remove old example projects
        old_projects = db.query(ProjectRecord).filter_by(owner_id=user.id).all()
        
        for old_proj in old_projects:
            logger.info(f"Removing old example project: {old_proj.name} (ID: {old_proj.id})")
            db.delete(old_proj)
        db.flush()

        # 3. Iterate over JSON files
        for file_path in sorted(EXAMPLES_DIR.glob("*.json")):
            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    example = ExampleProject(**data)

                logger.info(f"Creating example project: {example.project_name}")

                # 4. Create ProjectRecord (to get new project_id)
                new_project = ProjectRecord(
                    name=example.project_name,
                    owner_id=user.id,
                    workflow=example.workflow.model_dump(),  # Will be updated later with new data IDs
                    ui_state=example.ui_state.model_dump(),
                    thumb=base64.b64decode(example.thumb) if example.thumb else None,
                    show_in_explore=True,
                    updated_at=datetime.fromtimestamp(
                        example.updated_at / 1000, tz=timezone.utc
                    ),
                    created_at=datetime.fromtimestamp(
                        example.updated_at / 1000, tz=timezone.utc
                    ), # use updated_at as created_at as well
                )
                db.add(new_project)
                db.flush()  # Flush to get new_project.id
                logger.info(f"Created example project, ID: {new_project.id}, name: {new_project.name}")

                # 5. Restore Files
                for ex_file in example.files:
                    # Check if file key already exists (global uniqueness check)
                    # Since we use UUIDs, collision is rare, but if it exists, we assume it's the same file
                    existing_file = (
                        db.query(FileRecord).filter_by(file_key=ex_file.key).first()
                    )
                    if not existing_file:
                        # Insert DB record
                        db_file = FileRecord(
                            filename=ex_file.filename,
                            file_key=ex_file.key,
                            format=ex_file.format,
                            user_id=user.id,
                            project_id=new_project.id,
                            node_id=ex_file.node_id,
                            file_size=ex_file.file_size,
                        )
                        db.add(db_file)

                        # Upload to MinIO
                        # We bypass FileManager.write because we want to specify the key
                        content_bytes = base64.b64decode(ex_file.content)
                        file_manager.minio_client.put_object(
                            file_manager.bucket,
                            ex_file.key,
                            io.BytesIO(content_bytes),
                            length=len(content_bytes),
                        )

                # 6. Restore Data and Build ID Mapping
                id_map: dict[int, int] = {}  # old_id -> new_id
                for ex_data in example.datas:
                    data_bytes = base64.b64decode(ex_data.data)
                    new_data_record = NodeOutputRecord(
                        project_id=new_project.id,
                        node_id=ex_data.node_id,
                        port=ex_data.port,
                        data=data_bytes,
                    )
                    db.add(new_data_record)
                    db.flush()  # Get new ID
                    id_map[ex_data.old_id] = new_data_record.id # type: ignore

                # 7. Update Workflow with new Data IDs
                # We modify the workflow object in memory and then save it back
                current_workflow = example.workflow
                for node in current_workflow.nodes:
                    for port, data_ref in node.data_out.items():
                        if data_ref.data_id in id_map:
                            data_ref.data_id = id_map[data_ref.data_id]

                # Update the project record with the fixed workflow
                new_project.workflow = current_workflow.model_dump() # type: ignore

            except Exception as e:
                logger.error(
                    f"Failed to load example project from {file_path.name}: {e}"
                )
                raise e

        db.commit()


def persist_projects(project_name: str, new_name: str | None = None) -> None:
    """
    Export specified projects to JSON files, including files and data.
    """
    db_client = SessionLocal()
    file_manager = FileManager(sync_db_session=db_client)
    if new_name is not None and new_name.strip() == "":
        new_name = None

    # 1. Find Project
    project_record = (
        db_client.query(ProjectRecord).filter_by(name=project_name).first()
    )
    if not project_record:
        print(f"Project '{project_name}' not found.")
        return

    project_id = project_record.id
    project_data = get_project_by_id_sync(db_client, project_id, None) # type: ignore
    if not project_data:
        return

    print(f"Exporting project: {project_name} (ID: {project_id})...")

    # 2. Collect Files
    example_files = []
    file_records = (
        db_client.query(FileRecord)
        .filter_by(project_id=project_id, is_deleted=False)
        .all()
    )
    for fr in file_records:
        try:
            # Read content from MinIO
            content = file_manager.read_sync(
                file_manager.get_file_by_key_sync(fr.file_key), # type: ignore
                user_id=None,  # Admin read
            )
            example_files.append(
                ExampleFile(
                    key=fr.file_key, # type: ignore
                    filename=fr.filename, # type: ignore
                    format=fr.format, # type: ignore
                    node_id=fr.node_id, # type: ignore
                    file_size=fr.file_size, # type: ignore
                    content=base64.b64encode(content).decode("utf-8"),
                )
            )
        except Exception as e:
            print(f"Warning: Failed to export file {fr.filename}: {e}")

    # 3. Collect Data
    example_datas = []
    data_records = (
        db_client.query(NodeOutputRecord).filter_by(project_id=project_id).all()
    )
    for dr in data_records:
        example_datas.append(
            ExampleData(
                old_id=dr.id, # type: ignore
                node_id=dr.node_id, # type: ignore
                port=dr.port, # type: ignore
                data=base64.b64encode(dr.data).decode("utf-8"), # type: ignore
            )
        )

    # 4. Build ExampleProject
    new_project_name = project_name
    if new_name:
        new_project_name = new_name
    example_project = ExampleProject(
        project_name=new_project_name,
        updated_at=project_data.updated_at,
        thumb=project_data.thumb,
        editable=project_data.editable,
        workflow=project_data.workflow,
        ui_state=project_data.ui_state,
        files=example_files,
        datas=example_datas,
    )

    # 5. Save to JSON
    output_path = EXAMPLES_DIR / f"{new_project_name}.json"
    output_path.parent.mkdir(parents=True, exist_ok=True)

    with open(output_path, "w", encoding="utf-8") as f:
        f.write(example_project.model_dump_json(indent=4))

    print(f"Successfully exported '{project_name}' to '{output_path}'.")
    print(f"  - Files: {len(example_files)}")
    print(f"  - Data records: {len(example_datas)}")
