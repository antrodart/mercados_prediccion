from django.shortcuts import render, redirect, get_object_or_404
from .models import Market, Option, Asset
from django.db.models import Sum
from django.http import JsonResponse
import json

def ajax_total_buy_cost(request):
	market_id = request.GET.get('market_id', None)
	option_id = request.GET.get('option_id', None)
	quantity = int(request.GET.get('quantity', None))
	is_yes = "true" == request.GET.get('is_yes', None)

	cost = total_buy_cost(market_id, option_id, quantity, is_yes)
	json_dummy = {
		'cost': cost,
	}
	data = json.dumps(json_dummy)
	res = JsonResponse(data, safe=False)

	return res

def total_buy_cost(market_id, option_id, quantity, is_yes):
	market = Market.objects.get(pk=market_id)
	betting_option = Option.objects.get(pk=option_id)

	if market.is_binary:
		other_option = Option.objects.get(market=market, binary_yes=not betting_option.binary_yes)
		assets_sold_betting_option = Asset.objects.filter(option=betting_option).aggregate(Sum('quantity'))[
			'quantity__sum']
		assets_sold_other_option = Asset.objects.filter(option=other_option).aggregate(Sum('quantity'))['quantity__sum']
		cost = betting_option.get_todays_price().buy_price

		if assets_sold_betting_option is None:
			assets_sold_betting_option = 0
		if assets_sold_other_option is None:
			assets_sold_other_option = 0

		total_assets_sold = assets_sold_betting_option + assets_sold_other_option

		for i in range(quantity - 1):
			assets_sold_betting_option += 1
			total_assets_sold += 1
			rounded_cost = round((assets_sold_betting_option / total_assets_sold) * 100)
			if rounded_cost == 100:
				rounded_cost = 99
			elif rounded_cost == 0:
				rounded_cost = 1

			cost += rounded_cost
	elif market.is_exclusive:
		assets_sold_betting_option = Asset.objects.filter(option=betting_option).aggregate(Sum('quantity'))['quantity__sum']
		assets_sold_others_options = Asset.objects.filter(market=market).exclude(option=betting_option).aggregate(Sum('quantity'))['quantity__sum']
		cost = betting_option.get_todays_price().buy_price

		if assets_sold_betting_option is None:
			assets_sold_betting_option = 0
		if assets_sold_others_options is None:
			assets_sold_others_options = 0

		total_assets_sold = assets_sold_betting_option + assets_sold_others_options

		for i in range(quantity - 1):
			assets_sold_betting_option += 1
			total_assets_sold += 1
			rounded_cost = round((assets_sold_betting_option / total_assets_sold) * 100)
			if rounded_cost == 100:
				rounded_cost = 99
			elif rounded_cost == 0:
				rounded_cost = 1

			cost += rounded_cost
	else:
		assets_sold_betting_option = Asset.objects.filter(option=betting_option, is_yes=is_yes).aggregate(Sum('quantity'))['quantity__sum']
		assets_sold_other_option = Asset.objects.filter(option=betting_option, is_yes=not is_yes).aggregate(Sum('quantity'))['quantity__sum']
		if is_yes:
			cost = betting_option.get_todays_price_yes().buy_price
		else:
			cost = betting_option.get_todays_price_no().buy_price

		if assets_sold_betting_option is None:
			assets_sold_betting_option = 0
		if assets_sold_other_option is None:
			assets_sold_other_option = 0

		total_assets_sold = assets_sold_betting_option + assets_sold_other_option

		for i in range(quantity - 1):
			assets_sold_betting_option += 1
			total_assets_sold += 1
			rounded_cost = round((assets_sold_betting_option / total_assets_sold) * 100)
			if rounded_cost == 100:
				rounded_cost = 99
			elif rounded_cost == 0:
				rounded_cost = 1

			cost += rounded_cost

	return cost