from django.core.management.base import BaseCommand
from django.db import transaction
from users.models import User
from mercados_de_prediccion.models import Market, Price
import datetime

class Command(BaseCommand):
	help = 'This command adds the cron jobs to the schedule.'

	def handle(self, *args, **kwargs):
		self.stdout.write("Trying to register prices per day...")
		register_prices_per_day()


def register_prices_per_day():
	print("Registering prices. Current time: " + str(datetime.datetime.now()))
	today = datetime.datetime.now()
	markets_to_register_prices = Market.objects.filter(end_date__gte=today)  #Markets that haven't finished or finish today

	with transaction.atomic():
		for market in markets_to_register_prices:
			print("Registering prices for market: " + str(market))
			prices = Price.objects.filter(option__in=market.option_set.all(), is_last=True)
			for price in prices:
				overwrite_price(price)

	print("Register prices method finished.")

def overwrite_price(current_price):
	print("In the overwrite_prices method. Setting old price is_last to False, and saving it...")
	#  Now the previous "last prices" are no longer the last prices.
	current_price.is_last = False
	current_price.save()

	print("Going to create the new price, copying the old one and setting is_last to True.")
	#  Creation of 2 new prices, one for each option, that are the last prices.
	new_price = Price.objects.create(option=current_price.option, is_yes=current_price.is_yes, is_last=True, buy_price=current_price.buy_price)

	print("Price created. Price: " + str(new_price))
