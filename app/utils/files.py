IMAGE_EXTENSIONS = (".png", ".jpg", ".jpeg", ".webp")
ALLOWED_MIME_TYPES = {"image/png", "image/jpeg", "image/webp"}


def validate_image_files(file) -> bool:
    filename = file.filename
    if not filename:
        return False

    ext_valid = filename.lower().endswith(IMAGE_EXTENSIONS)
    mime_valid = file.content_type in ALLOWED_MIME_TYPES

    return ext_valid and mime_valid
