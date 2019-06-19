from .models import JoinedCommunity, Asset
from django.core.exceptions import PermissionDenied
from django.utils.translation import gettext_lazy as _
import calendar
import datetime


def add_months(sourcedate, months):
	month = sourcedate.month - 1 + months
	year = sourcedate.year + month // 12
	month = month % 12 + 1
	day = min(sourcedate.day, calendar.monthrange(year,month)[1])
	return datetime.date(year, month, day)


def check_user_is_member_of_community(user, community):
	if community:
		try:
			if not JoinedCommunity.objects.get(community_id=community.pk, user=user.pk).is_accepted:
				raise PermissionDenied(_("The market is part of a private community in which you do not have access."))
		except:
			raise PermissionDenied(_("The market is part of a private community in which you do not have access."))


def recalculate_price_options(option, asset):
	market = option.market
	price = None

	if not market.is_binary:
		num_assets_option_yes = option.asset_set.filter(is_yes=True)
		if asset.is_yes:
			print('TODO')
			# todo
	asset.save()