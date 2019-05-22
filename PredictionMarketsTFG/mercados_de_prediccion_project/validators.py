import os
import datetime
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _

def validate_file_image_extension(value):
	ext = os.path.splitext(value.name)[1]  # [0] returns path + filename
	valid_extensions = ['.png', '.jpg']
	if not ext.lower() in valid_extensions:
		raise ValidationError(_('Images must be in PNG or JPG format.'))


def validate_date_is_past(date):
	if date >= datetime.datetime.today().date():
		raise ValidationError(_('Date must be past.'))


def validate_date_is_future(date):
	if date <= datetime.datetime.today().date():
		raise ValidationError(_('Date must be future'))