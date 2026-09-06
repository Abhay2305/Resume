"""PROCS Template CMS Router.

Full CRUD endpoints for managing resume templates.
Includes file upload, versioning, publishing, and archival.
All routes require admin authentication.
"""
import hashlib
import json
import logging
import os
import uuid
from datetime import datetime
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query, Response, UploadFile, File
from sqlalchemy.orm import Session

from ..database import get_db
from ..auth import require_admin
from ..models.identity import User
from ..models.resume import Template, TemplateVersion
from ..schemas.procs_template import (
    TemplateCreate,
    TemplateUpdate,
    TemplateOut,
    TemplateListResponse,
    TemplateDetailResponse,
    TemplateActionResponse,
    TemplateReorderRequest,
    TemplateDuplicateRequest,
    UploadResponse,
    DefinitionUploadResponse,
    TemplateVersionOut,
    TemplateVersionListResponse,
)
from ..repositories.resume import TemplateRepository
from ..services.audit_service import AuditService

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/templates", tags=["PROCS Templates"])

# Allowed MIME types for uploads
ALLOWED_IMAGE_TYPES = {"image/jpeg", "image/png", "image/webp", "image/gif"}
ALLOWED_DOC_TYPES = {"application/json", "text/plain"}
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB


def _get_storage_dir() -> str:
    """Get or create the storage directory."""
    base = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "storage")
    os.makedirs(base, exist_ok=True)
    return base


def _safe_delete_asset(db: Session, relative_url: str, exclude_template_id: Optional[str] = None) -> None:
    """Delete a storage file only if no other template references it."""
    if not relative_url:
        return
    storage_dir = _get_storage_dir()
    filepath = os.path.join(storage_dir, relative_url.lstrip("/"))
    if not os.path.isfile(filepath):
        return
    query = db.query(Template).filter(Template.thumbnail_url == relative_url)
    if exclude_template_id:
        query = query.filter(Template.id != exclude_template_id)
    if query.first():
        return
    preview_query = db.query(Template).filter(Template.preview_images.isnot(None))
    for t in preview_query.all():
        if t.preview_images and relative_url in t.preview_images:
            if exclude_template_id and t.id == exclude_template_id:
                continue
            return
    try:
        os.remove(filepath)
        logger.info("Deleted orphan asset: %s", filepath)
    except OSError as e:
        logger.warning("Failed to delete asset %s: %s", filepath, e)


def _save_upload(file: UploadFile, subfolder: str) -> tuple[str, str, int]:
    """Save an uploaded file. Returns (relative_url, filename, size)."""
    storage_dir = _get_storage_dir()
    folder = os.path.join(storage_dir, subfolder)
    os.makedirs(folder, exist_ok=True)

    ext = os.path.splitext(file.filename or "upload")[1] or ".bin"
    filename = f"{uuid.uuid4().hex}{ext}"
    filepath = os.path.join(folder, filename)

    content = file.file.read()
    size = len(content)

    if size > MAX_FILE_SIZE:
        raise HTTPException(status_code=413, detail=f"File too large. Maximum size is {MAX_FILE_SIZE // (1024*1024)}MB")

    with open(filepath, "wb") as f:
        f.write(content)

    relative_url = f"/storage/{subfolder}/{filename}"
    return relative_url, filename, size


def _snapshot_template(template: Template) -> dict:
    """Create a snapshot dict of the template's current state."""
    return {
        "id": template.id,
        "name": template.name,
        "slug": template.slug,
        "description": template.description,
        "category": template.category,
        "thumbnail_url": template.thumbnail_url,
        "preview_images": template.preview_images,
        "color_scheme": template.color_scheme,
        "layout_schema": template.layout_schema,
        "template_definition": template.template_definition,
        "theme": template.theme,
        "fonts": template.fonts,
        "colors": template.colors,
        "status": template.status,
        "version": template.version,
        "author": template.author,
        "is_default": template.is_default,
        "sort_order": template.sort_order,
        "tags": template.tags,
        "metadata_json": template.metadata_json,
    }


# ---------------------------------------------------------------------------
# List / Detail
# ---------------------------------------------------------------------------

@router.get("")
def get_templates(
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    search: Optional[str] = Query(None),
    category: Optional[str] = Query(None),
    status: Optional[str] = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    """Get paginated template list with filters. Requires admin role."""
    repo = TemplateRepository(db)
    items, total = repo.get_paginated(
        page=page, limit=limit, search=search, category=category, status=status,
    )
    return TemplateListResponse(
        items=[TemplateOut.model_validate(t) for t in items],
        total=total,
        page=page,
        limit=limit,
        totalPages=max(1, -(-total // limit)),
    )


@router.get("/published")
def get_published_templates(
    db: Session = Depends(get_db),
):
    """Get all published templates. Public endpoint for Prompt Resume frontend."""
    repo = TemplateRepository(db)
    templates = repo.get_published()
    items = [TemplateOut.model_validate(t) for t in templates]
    response_data = TemplateListResponse(
        items=items,
        total=len(templates),
    )

    etag_payload = json.dumps([t.model_dump() for t in items], sort_keys=True, default=str)
    etag = hashlib.sha256(etag_payload.encode()).hexdigest()[:32]
    last_modified = max(
        (t.updated_at or t.created_at for t in templates),
        default=datetime.utcnow(),
    ).strftime("%a, %d %b %Y %H:%M:%S GMT")

    return Response(
        content=json.dumps(response_data.model_dump(), default=str),
        media_type="application/json",
        headers={
            "Cache-Control": "public, max-age=300, stale-while-revalidate=60",
            "ETag": f'"{etag}"',
            "Last-Modified": last_modified,
        },
    )


@router.get("/stats")
def get_template_stats(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    """Get template usage statistics. Requires admin role."""
    repo = TemplateRepository(db)
    templates = repo.get_all_templates()
    return {
        "success": True,
        "items": [
            {
                "id": t.id,
                "name": t.name,
                "category": t.category,
                "usage_count": t.usage_count or 0,
            }
            for t in templates
        ],
    }


@router.get("/{template_id}")
def get_template(
    template_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    """Get template detail by ID. Requires admin role."""
    repo = TemplateRepository(db)
    template = repo.get(template_id)
    if not template:
        raise HTTPException(status_code=404, detail="Template not found")
    return TemplateDetailResponse(data=TemplateOut.model_validate(template))


# ---------------------------------------------------------------------------
# CRUD
# ---------------------------------------------------------------------------

@router.post("")
def create_template(
    body: TemplateCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    """Create a new template. Requires admin role."""
    repo = TemplateRepository(db)

    # Check duplicate ID
    if repo.get(body.id):
        raise HTTPException(status_code=409, detail=f"Template with ID '{body.id}' already exists")

    # Validate slug uniqueness
    slug = body.slug or body.id.lower().replace(" ", "-")
    if repo.slug_exists(slug):
        raise HTTPException(status_code=409, detail=f"Slug '{slug}' already exists")

    template = repo.create({
        "id": body.id,
        "name": body.name,
        "slug": slug,
        "description": body.description,
        "category": body.category,
        "color_scheme": body.color_scheme,
        "layout_schema": body.layout_schema,
        "template_definition": body.template_definition,
        "theme": body.theme,
        "fonts": body.fonts,
        "colors": body.colors,
        "author": body.author,
        "is_default": body.is_default,
        "sort_order": body.sort_order,
        "tags": body.tags,
        "metadata_json": body.metadata_json,
        "status": "draft",
        "version": 1,
        "usage_count": 0,
    })

    audit = AuditService(db)
    audit.log_create(
        entity_type="template",
        entity_id=template.id,
        description=f"Created template '{template.name}'",
    )

    return TemplateDetailResponse(data=TemplateOut.model_validate(template))


@router.put("/{template_id}")
def update_template(
    template_id: str,
    body: TemplateUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    """Update template metadata. Requires admin role."""
    repo = TemplateRepository(db)
    template = repo.get(template_id)
    if not template:
        raise HTTPException(status_code=404, detail="Template not found")

    update_data = body.model_dump(exclude_unset=True)

    # Validate slug uniqueness if changed
    if "slug" in update_data and update_data["slug"]:
        if repo.slug_exists(update_data["slug"], exclude_id=template_id):
            raise HTTPException(status_code=409, detail=f"Slug '{update_data['slug']}' already exists")

    # Increment version if template_definition is changing
    definition_changed = "template_definition" in update_data and update_data["template_definition"] != template.template_definition
    if definition_changed:
        update_data["version"] = template.version + 1

    template = repo.update(template, update_data)

    audit = AuditService(db)
    audit.log_update(
        entity_type="template",
        entity_id=template_id,
        new_state=update_data,
        description=f"Updated template '{template.name}'" + (" (definition changed, version incremented)" if definition_changed else ""),
    )

    return TemplateDetailResponse(data=TemplateOut.model_validate(template))


@router.delete("/{template_id}")
def delete_template(
    template_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    """Delete a template and its uploaded files. Requires admin role."""
    repo = TemplateRepository(db)
    template = repo.get(template_id)
    if not template:
        raise HTTPException(status_code=404, detail="Template not found")

    name = template.name

    # Clean up uploaded files before deleting the DB row
    storage_dir = _get_storage_dir()
    files_deleted = []

    # Delete thumbnail
    if template.thumbnail_url:
        thumb_path = os.path.join(storage_dir, template.thumbnail_url.lstrip("/"))
        if os.path.isfile(thumb_path):
            os.remove(thumb_path)
            files_deleted.append(thumb_path)

    # Delete preview images
    if template.preview_images:
        for url in template.preview_images:
            preview_path = os.path.join(storage_dir, url.lstrip("/"))
            if os.path.isfile(preview_path):
                os.remove(preview_path)
                files_deleted.append(preview_path)

    if files_deleted:
        logger.info("Cleaned up %d files for template '%s': %s", len(files_deleted), name, files_deleted)

    repo.delete(template_id)

    audit = AuditService(db)
    audit.log_delete(
        entity_type="template",
        entity_id=template_id,
        description=f"Deleted template '{name}'",
    )

    return TemplateActionResponse(message=f"Template '{name}' deleted")


# ---------------------------------------------------------------------------
# Status Actions
# ---------------------------------------------------------------------------

@router.post("/{template_id}/publish")
def publish_template(
    template_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    """Publish a template. Requires admin role."""
    repo = TemplateRepository(db)
    template = repo.get(template_id)
    if not template:
        raise HTTPException(status_code=404, detail="Template not found")

    # Save version snapshot before publishing (only if one doesn't already exist for this version)
    existing = db.query(TemplateVersion).filter(
        TemplateVersion.template_id == template_id,
        TemplateVersion.version == template.version,
    ).first()

    if not existing:
        snapshot = _snapshot_template(template)
        version_record = TemplateVersion(
            template_id=template_id,
            version=template.version,
            snapshot=snapshot,
        )
        db.add(version_record)

    template.status = "published"
    template.published_at = datetime.utcnow()
    db.commit()
    db.refresh(template)

    audit = AuditService(db)
    audit.log_update(
        entity_type="template",
        entity_id=template_id,
        new_state={"status": "published"},
        description=f"Published template '{template.name}' v{template.version}",
    )

    return TemplateActionResponse(message=f"Template '{template.name}' published")


@router.post("/{template_id}/archive")
def archive_template(
    template_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    """Archive a template. Requires admin role."""
    repo = TemplateRepository(db)
    template = repo.get(template_id)
    if not template:
        raise HTTPException(status_code=404, detail="Template not found")

    template.status = "archived"
    db.commit()

    audit = AuditService(db)
    audit.log_update(
        entity_type="template",
        entity_id=template_id,
        new_state={"status": "archived"},
        description=f"Archived template '{template.name}'",
    )

    return TemplateActionResponse(message=f"Template '{template.name}' archived")


@router.post("/{template_id}/deprecate")
def deprecate_template(
    template_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    """Deprecate a template. Requires admin role."""
    repo = TemplateRepository(db)
    template = repo.get(template_id)
    if not template:
        raise HTTPException(status_code=404, detail="Template not found")

    template.status = "deprecated"
    db.commit()

    audit = AuditService(db)
    audit.log_update(
        entity_type="template",
        entity_id=template_id,
        new_state={"status": "deprecated"},
        description=f"Deprecated template '{template.name}'",
    )

    return TemplateActionResponse(message=f"Template '{template.name}' deprecated")


# ---------------------------------------------------------------------------
# Versioning
# ---------------------------------------------------------------------------

@router.get("/{template_id}/versions")
def get_template_versions(
    template_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    """Get version history for a template. Requires admin role."""
    repo = TemplateRepository(db)
    if not repo.get(template_id):
        raise HTTPException(status_code=404, detail="Template not found")

    versions = (
        db.query(TemplateVersion)
        .filter(TemplateVersion.template_id == template_id)
        .order_by(TemplateVersion.version.desc())
        .all()
    )

    return TemplateVersionListResponse(
        items=[TemplateVersionOut.model_validate(v) for v in versions],
        total=len(versions),
    )


@router.post("/{template_id}/versions/{version_id}/restore")
def restore_version(
    template_id: str,
    version_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    """Restore a template to a previous version. Requires admin role."""
    repo = TemplateRepository(db)
    template = repo.get(template_id)
    if not template:
        raise HTTPException(status_code=404, detail="Template not found")

    version = db.query(TemplateVersion).filter(
        TemplateVersion.id == version_id,
        TemplateVersion.template_id == template_id,
    ).first()
    if not version:
        raise HTTPException(status_code=404, detail="Version not found")

    snapshot = version.snapshot
    template.name = snapshot.get("name", template.name)
    template.description = snapshot.get("description", template.description)
    template.category = snapshot.get("category", template.category)
    template.color_scheme = snapshot.get("color_scheme", template.color_scheme)
    template.layout_schema = snapshot.get("layout_schema", template.layout_schema)
    template.template_definition = snapshot.get("template_definition", template.template_definition)
    template.theme = snapshot.get("theme", template.theme)
    template.fonts = snapshot.get("fonts", template.fonts)
    template.colors = snapshot.get("colors", template.colors)
    template.version = template.version + 1
    db.commit()

    audit = AuditService(db)
    audit.log_update(
        entity_type="template",
        entity_id=template_id,
        description=f"Restored template '{template.name}' to version {version.version}",
    )

    return TemplateDetailResponse(data=TemplateOut.model_validate(template))


# ---------------------------------------------------------------------------
# Duplicate
# ---------------------------------------------------------------------------

@router.post("/{template_id}/duplicate")
def duplicate_template(
    template_id: str,
    body: TemplateDuplicateRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    """Duplicate a template. Requires admin role."""
    repo = TemplateRepository(db)
    source = repo.get(template_id)
    if not source:
        raise HTTPException(status_code=404, detail="Template not found")

    if repo.get(body.new_id):
        raise HTTPException(status_code=409, detail=f"Template with ID '{body.new_id}' already exists")

    new_template = repo.create({
        "id": body.new_id,
        "name": body.new_name or f"{source.name} (Copy)",
        "slug": body.new_id.lower().replace(" ", "-"),
        "description": source.description,
        "category": source.category,
        "thumbnail_url": source.thumbnail_url,
        "preview_images": source.preview_images,
        "color_scheme": source.color_scheme,
        "layout_schema": source.layout_schema,
        "template_definition": source.template_definition,
        "theme": source.theme,
        "fonts": source.fonts,
        "colors": source.colors,
        "status": "draft",
        "version": 1,
        "author": source.author,
        "is_default": False,
        "sort_order": source.sort_order + 1,
        "tags": source.tags,
        "usage_count": 0,
        "metadata_json": source.metadata_json,
    })

    audit = AuditService(db)
    audit.log_create(
        entity_type="template",
        entity_id=new_template.id,
        description=f"Duplicated template '{source.name}' to '{new_template.name}'",
    )

    return TemplateDetailResponse(data=TemplateOut.model_validate(new_template))


# ---------------------------------------------------------------------------
# Reorder
# ---------------------------------------------------------------------------

@router.post("/reorder")
def reorder_templates(
    body: TemplateReorderRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    """Reorder templates. Requires admin role."""
    repo = TemplateRepository(db)
    repo.reorder(body.template_ids)
    return TemplateActionResponse(message="Templates reordered")


# ---------------------------------------------------------------------------
# File Upload
# ---------------------------------------------------------------------------

@router.post("/{template_id}/upload/thumbnail")
async def upload_thumbnail(
    template_id: str,
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    """Upload thumbnail for a template. Requires admin role."""
    repo = TemplateRepository(db)
    template = repo.get(template_id)
    if not template:
        raise HTTPException(status_code=404, detail="Template not found")

    if file.content_type not in ALLOWED_IMAGE_TYPES:
        raise HTTPException(status_code=400, detail=f"Invalid file type. Allowed: {', '.join(ALLOWED_IMAGE_TYPES)}")

    url, filename, size = _save_upload(file, "templates/thumbnails")

    _safe_delete_asset(db, template.thumbnail_url, exclude_template_id=template_id)
    template.thumbnail_url = url
    db.commit()

    return UploadResponse(url=url, filename=filename, size=size)


@router.post("/{template_id}/upload/preview")
async def upload_preview_image(
    template_id: str,
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    """Upload a preview image for a template. Requires admin role."""
    repo = TemplateRepository(db)
    template = repo.get(template_id)
    if not template:
        raise HTTPException(status_code=404, detail="Template not found")

    if file.content_type not in ALLOWED_IMAGE_TYPES:
        raise HTTPException(status_code=400, detail=f"Invalid file type. Allowed: {', '.join(ALLOWED_IMAGE_TYPES)}")

    url, filename, size = _save_upload(file, "templates/previews")

    # Append to preview_images list
    if not template.preview_images:
        template.preview_images = []
    template.preview_images.append(url)
    db.commit()

    return UploadResponse(url=url, filename=filename, size=size)


@router.post("/{template_id}/upload/definition")
async def upload_template_definition(
    template_id: str,
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    """Upload template definition JSON. Stored in database, not filesystem. Requires admin role."""
    repo = TemplateRepository(db)
    template = repo.get(template_id)
    if not template:
        raise HTTPException(status_code=404, detail="Template not found")

    if file.content_type not in ALLOWED_DOC_TYPES:
        raise HTTPException(status_code=400, detail=f"Invalid file type. Allowed: {', '.join(ALLOWED_DOC_TYPES)}")

    content = await file.read()
    try:
        definition = json.loads(content)
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid JSON file")

    template.template_definition = definition
    template.version = template.version + 1
    db.commit()

    return DefinitionUploadResponse(
        definition_stored=True,
        filename=file.filename or "definition.json",
        size=len(content),
    )


# ---------------------------------------------------------------------------
# Usage Tracking
# ---------------------------------------------------------------------------

@router.post("/{template_id}/usage")
def increment_usage(
    template_id: str,
    db: Session = Depends(get_db),
):
    """Increment template usage count. Public endpoint for Prompt Resume frontend."""
    repo = TemplateRepository(db)
    repo.increment_usage(template_id)
    return {"success": True}
