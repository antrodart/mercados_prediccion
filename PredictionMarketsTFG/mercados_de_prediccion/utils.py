from .models import JoinedCommunity, Asset, Price
from django.db.models import Sum
from django.core.exceptions import PermissionDenied
from django.utils.translation import gettext_lazy as _
import calendar
import datetime


def add_months(sourcedate, months):
	month = sourcedate.month - 1 + months
	year = sourcedate.year + month // 12
	month = month % 12 + 1
	day = min(sourcedate.day, calendar.monthrange(year, month)[1])
	return datetime.date(year, month, day)


def check_user_is_member_of_community(user, community):
	if community:
		try:
			if not JoinedCommunity.objects.get(community_id=community.pk, user=user.pk).is_accepted:
				raise PermissionDenied(_("The market is part of a private community in which you do not have access."))
		except:
			raise PermissionDenied(_("The market is part of a private community in which you do not have access."))


def user_subtract_karma(user, asset, community):
	joined_community = None
	if asset.option.market.is_binary:
		buy_price = asset.option.get_todays_price().buy_price
	elif asset.is_yes:
		buy_price = asset.option.get_todays_price_yes().buy_price
	else:
		buy_price = asset.option.get_todays_price_no().buy_price

	if community:
		joined_community = JoinedCommunity.objects.get(user=user, community=community).private_karma
		karma = joined_community.private_karma
	else:
		karma = user.public_karma

	total_buy_price = buy_price * asset.quantity

	if total_buy_price > karma:
		raise ValueError("There was a problem with the assets buy: You don't have enough karma.")

	if community:
		joined_community.private_karma = joined_community.private_karma - total_buy_price
		joined_community.save()
	else:
		user.public_karma = user.public_karma - total_buy_price
		user.save()


def recalculate_price_options(option, asset):
	if option.market.is_binary:
		other_option = option.market.option_set.get(binary_yes=not option.binary_yes)
		betting_option_price = option.get_todays_price()
		other_option_price = other_option.get_todays_price()
		total_assets_betting_option = Asset.objects.filter(option=option).aggregate(Sum('quantity'))['quantity__sum']
		total_assets_other_option = Asset.objects.filter(option=other_option).aggregate(Sum('quantity'))['quantity__sum']
		user_option_asset = Asset.objects.filter(user=asset.user, option=option)
	else:
		total_assets_betting_option = Asset.objects.filter(option=option, is_yes=asset.is_yes).aggregate(Sum('quantity'))['quantity__sum']
		total_assets_other_option = Asset.objects.filter(option=option, is_yes=not asset.is_yes).aggregate(Sum('quantity'))['quantity__sum']
		if asset.is_yes:
			betting_option_price = option.get_todays_price_yes()
			other_option_price = option.get_todays_price_no()
		else:
			betting_option_price = option.get_todays_price_no()
			other_option_price = option.get_todays_price_yes()
		user_option_asset = Asset.objects.filter(user=asset.user, option=option, is_yes=asset.is_yes)

	if total_assets_betting_option is None:
		total_assets_betting_option = 0
	if total_assets_other_option is None:
		total_assets_other_option = 0

	#  We can sum the quantity we are buying to the total_assets_betting_option, which will give us the updated price
	total_assets_betting_option += asset.quantity

	#  Finally, we divide these quantities by the sum of them to obtain the percentage (which is the price)
	total_assets = total_assets_betting_option + total_assets_other_option
	buy_price_betting_option = round((total_assets_betting_option / total_assets) * 100)
	buy_price_other_option = round((total_assets_other_option / total_assets) * 100)

	#  Assert that no price is 0 or 100.
	if buy_price_betting_option == 100:
		buy_price_betting_option = 99
	if buy_price_betting_option == 0:
		buy_price_betting_option = 1
	if buy_price_other_option == 100:
		buy_price_other_option = 99
	if buy_price_other_option == 0:
		buy_price_other_option = 1

	betting_option_price.buy_price = buy_price_betting_option
	other_option_price.buy_price = buy_price_other_option
	betting_option_price.save()
	other_option_price.save()

	#  Saving the asset
	if user_option_asset.exists():
		#  Updates the asset object that the user already has, adding the quantity.
		previous_asset = user_option_asset.first()
		previous_asset.quantity = previous_asset.quantity + asset.quantity
		previous_asset.save()
	else:
		#  Create new asset associated to the user and option, and saves it.
		asset.save()
