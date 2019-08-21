from .models import JoinedCommunity, Asset, Price
from django.db.models import Sum, F, Value
from django.db.models.functions import Coalesce
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


def check_market_has_not_expired(market):
	if market.has_expired:
		raise PermissionDenied(_("The market has ended and you can no longer place bets."))

def check_user_is_member_of_community(user, community):
	if community:
		try:
			if not JoinedCommunity.objects.get(community_id=community.pk, user=user.pk).is_accepted:
				raise PermissionDenied(_("The market is part of a private community in which you do not have access."))
		except:
			raise PermissionDenied(_("The market is part of a private community in which you do not have access."))


def check_user_has_enough_karma(buy_price, user_karma):
	if buy_price > user_karma:
		raise ValueError("There was a problem with the assets buy: You don't have enough karma.")


def user_subtract_karma(user, asset, community, market):
	if market.is_binary or market.is_exclusive:
		buy_price = asset.option.get_todays_price().buy_price
	elif asset.is_yes:
		buy_price = asset.option.get_todays_price_yes().buy_price
	else:
		buy_price = asset.option.get_todays_price_no().buy_price
	total_buy_price = buy_price * asset.quantity

	if community:
		joined_community = JoinedCommunity.objects.get(user=user, community=community)
		karma = joined_community.private_karma
		check_user_has_enough_karma(buy_price=total_buy_price, user_karma=karma)
		joined_community.private_karma = F('private_karma') - total_buy_price
		joined_community.save()
	else:
		karma = user.public_karma
		check_user_has_enough_karma(buy_price=total_buy_price, user_karma=karma)
		user.public_karma = F('public_karma') - total_buy_price
		user.save()


def save_asset_queryset_to_user(asset_queryset, new_asset):
	#  Saving the asset
	if asset_queryset.exists():
		#  Updates the asset object that the user already has, adding the quantity.
		previous_asset = asset_queryset.first()
		previous_asset.quantity = F('quantity') + new_asset.quantity
		previous_asset.save()
	else:
		#  Create new asset associated to the user and option, and saves it.
		new_asset.save()


def recalculate_price_binary_options(option, asset):
	if option.market.is_binary:
		other_option = option.market.option_set.get(binary_yes=not option.binary_yes)
		betting_option_price = option.get_todays_price()
		other_option_price = other_option.get_todays_price()
		total_assets_betting_option = Asset.objects.filter(option=option).aggregate(Sum('quantity'))['quantity__sum']
		total_assets_other_option = Asset.objects.filter(option=other_option).aggregate(Sum('quantity'))['quantity__sum']
		user_option_assets = Asset.objects.filter(user=asset.user, option=option)
	else:  #  Market is multiple non exclusive
		total_assets_betting_option = Asset.objects.filter(option=option, is_yes=asset.is_yes).aggregate(Sum('quantity'))['quantity__sum']
		total_assets_other_option = Asset.objects.filter(option=option, is_yes=not asset.is_yes).aggregate(Sum('quantity'))['quantity__sum']
		if asset.is_yes:
			betting_option_price = option.get_todays_price_yes()
			other_option_price = option.get_todays_price_no()
		else:
			betting_option_price = option.get_todays_price_no()
			other_option_price = option.get_todays_price_yes()
		user_option_assets = Asset.objects.filter(user=asset.user, option=option, is_yes=asset.is_yes)

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
	elif buy_price_betting_option == 0:
		buy_price_betting_option = 1
	if buy_price_other_option == 0:
		buy_price_other_option = 1
	elif buy_price_other_option == 100:
		buy_price_other_option = 99

	betting_option_price.buy_price = buy_price_betting_option
	other_option_price.buy_price = buy_price_other_option
	betting_option_price.save()
	other_option_price.save()

	#  Saving the asset
	save_asset_queryset_to_user(asset_queryset=user_option_assets, new_asset=asset)


def recalculate_price_exclusive_options(market, option, asset):
	user_option_assets = Asset.objects.filter(user=asset.user, option=option)
	total_assets_market = Asset.objects.filter(market=market).aggregate(quantity__sum=Coalesce(Sum('quantity'),Value(0)))['quantity__sum'] + asset.quantity

	assets_current_option = Asset.objects.filter(option=option).aggregate(quantity__sum=Coalesce(Sum('quantity'),Value(0)))['quantity__sum'] + asset.quantity
	buy_price_current_option = round((assets_current_option / total_assets_market)*100)
	price_current_option = option.get_todays_price()
	if buy_price_current_option == 100:
		buy_price_current_option = 99
	elif buy_price_current_option == 0:
		buy_price_current_option = 1
	price_current_option.buy_price = buy_price_current_option
	price_current_option.save()

	other_options = market.option_set.exclude(pk=option.pk).filter(price__is_last=True).annotate(assets_quantity=Coalesce(Sum('asset__quantity'),Value(0)))
	for other_option in other_options:
		buy_price_other_option = round((other_option.assets_quantity/total_assets_market)*100)
		other_option_price = other_option.get_todays_price()
		if buy_price_other_option == 0:
			buy_price_other_option = 1
		elif buy_price_other_option == 100:
			buy_price_other_option = 99
		other_option_price.buy_price = buy_price_other_option
		other_option_price.save()

	#  Saving the asset
	save_asset_queryset_to_user(asset_queryset=user_option_assets, new_asset=asset)


def pay_winner_option(option, non_exclusive_market, is_yes):
	if non_exclusive_market:
		assets = option.asset_set.filter(is_yes=is_yes)
	else:
		assets = option.asset_set.all()

	if option.market.community:
		for asset in assets:
			joined_community = JoinedCommunity.objects.get(user=asset.user, community=asset.market.community)
			joined_community.private_karma = F('private_karma') + (asset.quantity * 100)
			joined_community.save()
	else:
		for asset in assets:
			user = asset.user
			user.public_karma = F('public_karma') + (asset.quantity * 100)
			user.save()