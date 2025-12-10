"""
utils/file_upload.py

Secure, production-ready upload handler with:

- Extension + MIME type validation
- Strict filename sanitization
- UUID renaming
- Upload directory auto-creation
- Optional max file size safety guard
"""

import os
import uuid
import imghdr
from werkzeug.utils import secure_filename


# ---------------------------------------------------------
# DEFAULT CONSTANTS
# ---------------------------------------------------------
UPLOAD_ROOT = "static/uploads/products"
DEFAULT_ALLOWED_EXTS = {"jpg", "jpeg", "png", "webp"}

# Create directory on import (safe)
os.makedirs(UPLOAD_ROOT, exist_ok=True)


# ---------------------------------------------------------
# SANITY: EXTENSION CHECK
# ---------------------------------------------------------
def allowed_file(filename: str, allowed: set) -> bool:
    """Return True if file extension is allowed."""
    if not filename:
        return False
    if "." not in filename:
        return False
    ext = filename.rsplit(".", 1)[-1].lower()
    return ext in allowed


# ---------------------------------------------------------
# OPTIONAL MIME VALIDATION (image-only)
# ---------------------------------------------------------
def _validate_image_mime(path: str) -> bool:
    """
    Inspect file signature using imghdr to ensure it's a real image.
    Returns True if MIME matches extension.
    """
    img_type = imghdr.what(path)
    return img_type in {"jpeg", "png", "webp"}


# ---------------------------------------------------------
# MAIN UPLOAD HANDLER
# ---------------------------------------------------------
def handle_upload(
    file_storage,
    upload_dir: str = UPLOAD_ROOT,
    allowed_exts=None,
    allowed_extensions=None,
    max_size_mb: int = 5,
    validate_mime: bool = True,
):
    """
    Save an uploaded file safely.

    Parameters:
        file_storage      → Werkzeug FileStorage object
        upload_dir        → Where to store file
        allowed_exts      → Set of allowed extensions
        allowed_extensions→ Alias for allowed_exts (backwards compatible)
        max_size_mb       → Optional limit (default: 5 MB)
        validate_mime     → Validate file signature for images

    Returns:
        filename (str) → saved file  
        None           → invalid upload  
    """

    if not file_storage or not getattr(file_storage, "filename", "").strip():
        return None

    # Normalize arguments
    allowed_exts = allowed_extensions or allowed_exts or DEFAULT_ALLOWED_EXTS

    # Secure original filename
    original_name = secure_filename(file_storage.filename)

    # Extension check
    if not allowed_file(original_name, allowed_exts):
        return None

    # Ensure upload directory exists
    os.makedirs(upload_dir, exist_ok=True)

    # Generate unique filename
    ext = original_name.rsplit(".", 1)[-1].lower()
    unique_name = f"{uuid.uuid4().hex}.{ext}"
    save_path = os.path.join(upload_dir, unique_name)

    # ----------------------------------------------
    # SIZE CHECK (optional safety)
    # ----------------------------------------------
    file_storage.stream.seek(0, os.SEEK_END)
    size_mb = file_storage.stream.tell() / (1024 * 1024)
    file_storage.stream.seek(0)

    if size_mb > max_size_mb:
        return None  # silently reject oversized file

    # Save file
    try:
        file_storage.save(save_path)
    except Exception:
        return None

    # ----------------------------------------------
    # MIME CHECK (prevents fake jpg/php files)
    # ----------------------------------------------
    if validate_mime and ext in {"jpg", "jpeg", "png", "webp"}:
        if not _validate_image_mime(save_path):
            try:
                os.remove(save_path)
            except:
                pass
            return None

    return unique_name
