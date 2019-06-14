from .models import JoinedGroup
from django.core.exceptions import PermissionDenied
import calendar
import datetime


def add_months(sourcedate, months):
	month = sourcedate.month - 1 + months
	year = sourcedate.year + month // 12
	month = month % 12 + 1
	day = min(sourcedate.day, calendar.monthrange(year,month)[1])
	return datetime.date(year, month, day)


def check_user_is_member_of_group(user, group):
	try:
		if not JoinedGroup.objects.get(group_id=group.pk, user=user.pk).is_accepted:
			raise PermissionDenied(_("The market is part of a private group in which you do not have access."))
	except:
		raise PermissionDenied(_("The market is part of a private group in which you do not have access."))