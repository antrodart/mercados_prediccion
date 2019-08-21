from django import template
from django.db.models import Sum
from mercados_de_prediccion.models import Asset, Market, Option

register = template.Library()


@register.simple_tag()
def get_total_buy_cost(market_id, option_id, quantity, is_yes):
	market = Market.objects.get(pk=market_id)
	betting_option = Option.objects.get(pk=option_id)

	if market.is_binary:
		other_option = Option.objects.get(market=market, binary_yes= not betting_option.binary_yes)
		assets_sold_betting_option = Asset.objects.filter(option=betting_option).aggregate(Sum('quantity'))['quantity__sum']
		assets_sold_other_option = Asset.objects.filter(option=other_option).aggregate(Sum('quantity'))['quantity__sum']
		cost = betting_option.get_todays_price()

		if assets_sold_betting_option is None:
			assets_sold_betting_option = 0
		if assets_sold_other_option is None:
			assets_sold_other_option = 0

		total_assets_sold = assets_sold_betting_option + assets_sold_other_option

		for i in range(quantity - 1):
			assets_sold_betting_option += 1
			total_assets_sold += 1

			cost += round((assets_sold_betting_option / total_assets_sold) * 100)
		return cost
	elif market.is_exclusive:
		assets_sold_betting_option = Asset.objects.filter(option=betting_option).aggregate(Sum('quantity'))['quantity__sum']
		assets_sold_others_options = Asset.objects.filter(option=not betting_option, market=market).aggregate(Sum('quantity'))['quantity__sum']
		cost = betting_option.get_todays_price()

		if assets_sold_betting_option is None:
			assets_sold_betting_option = 0
		if assets_sold_others_options is None:
			assets_sold_others_options = 0

		total_assets_sold = assets_sold_betting_option + assets_sold_others_options

		for i in range(quantity - 1):
			assets_sold_betting_option += 1
			total_assets_sold += 1

			cost += round((assets_sold_betting_option / total_assets_sold) * 100)
		return cost
	else:
		assets_sold_betting_option = Asset.objects.filter(option=betting_option, is_yes=is_yes).aggregate(Sum('quantity'))['quantity__sum']
		assets_sold_other_option = Asset.objects.filter(option=betting_option, is_yes=not is_yes).aggregate(Sum('quantity'))['quantity__sum']
		if is_yes:
			cost = betting_option.get_todays_price_yes()
		else:
			cost = betting_option.get_todays_price_no()

		if assets_sold_betting_option is None:
			assets_sold_betting_option = 0
		if assets_sold_other_option is None:
			assets_sold_other_option = 0

		total_assets_sold = assets_sold_betting_option + assets_sold_other_option

		for i in range(quantity - 1):
			assets_sold_betting_option += 1
			total_assets_sold += 1

			cost += round((assets_sold_betting_option / total_assets_sold) * 100)
		return cost