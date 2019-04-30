from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
import datetime


def validate_date_of_birth(date_of_birth):
	if date_of_birth >= datetime.datetime.today().date():
		raise ValidationError(_('Date of birth must be in the past'))