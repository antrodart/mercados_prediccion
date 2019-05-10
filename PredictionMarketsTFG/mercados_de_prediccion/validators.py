import os
from django.core.exceptions import ValidationError

def validate_file_image_extension(value):
	ext = os.path.splitext(value.name)[1]  # [0] returns path + filename
	valid_extensions = ['.png', '.jpg']
	if not ext.lower() in valid_extensions:
		raise ValidationError(_('Images must be in PNG or JPG format.'))