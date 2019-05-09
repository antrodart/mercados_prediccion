from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
import datetime


def validate_date_is_past(date):
	if date >= datetime.datetime.today().date():
		raise ValidationError(_('Date of birth must be in the past'))
