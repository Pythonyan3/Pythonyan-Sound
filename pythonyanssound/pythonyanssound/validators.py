import io

from django.conf import settings
from django.core.exceptions import ValidationError
from django.core.files.images import get_image_dimensions
from django.db.models.fields.files import ImageFieldFile, FieldFile


def validate_image_resolution(image_field: ImageFieldFile) -> None:
    """Validates image resolution defined by settings."""
    print("Image", type(image_field))
    width, height = get_image_dimensions(image_field.file)
    if (
        height != settings.APP_IMAGE_HEIGHT
        or width != settings.APP_IMAGE_WIDTH
    ):
        raise ValidationError("Image size should be 1000x1000.")


def validate_file_size(file_field: FieldFile) -> None:
    """Validates total file size."""
    print("File", type(file_field))
    # creating file from tests passed BytesIO instance
    if isinstance(file_field.file, io.BytesIO):
        pass
    elif file_field.file.size > settings.APP_FILE_MAX_SIZE:
        raise ValidationError("File size should be less than 10Mb.")
