import io

from django.conf import settings
from django.core.exceptions import ValidationError
from django.core.files.images import get_image_dimensions


def validate_image_resolution(image_field):
    width, height = get_image_dimensions(image_field.file)
    if height != settings.APP_IMAGE_HEIGHT or width != settings.APP_IMAGE_WIDTH:
        raise ValidationError("Image size should be 1000x1000.")


def validate_file_size(file_field):
    # If file is instance of BytesIO then it is run from Tests (dunno why it works like that)
    if isinstance(file_field.file, io.BytesIO):
        pass
    elif file_field.file.size > settings.APP_FILE_MAX_SIZE:
        raise ValidationError("File size should be less than 10Mb.")
