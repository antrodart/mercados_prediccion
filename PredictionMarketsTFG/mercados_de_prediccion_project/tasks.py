from apscheduler.schedulers.background import BackgroundScheduler
from django.db import transaction
from users.models import User
from mercados_de_prediccion.models import Market, Price
import datetime
import logging


scheduler = BackgroundScheduler()


@scheduler.scheduled_job("cron", hour=0, minute=5, id="delete_users_marked")
def delete_users_marked():
	print("Deleting users")
	today = datetime.datetime.now()
	users_marked_deletion = User.objects.filter(deletion_date=today)

	for user in users_marked_deletion:
		print("Deleting user " + user.__str__())
		user.delete()


@scheduler.scheduled_job("cron", hour=14, minute=30, id="register_prices_per_day")
def register_prices_per_day():
	print("Registering prices. Current time: " + str(datetime.datetime.now()))
	logging.info('Registering prices')
	today = datetime.datetime.now()
	markets_to_register_prices = Market.objects.filter(end_date__gte=today)  #Markets that haven't finished or finish today

	for market in markets_to_register_prices:
		print("Entring the for loop for market: " + str(market))
		if market.is_binary:  #  Binary markets
			print("Market is binary")
			yes_option = market.option_set.get(binary_yes=True)
			no_option = market.option_set.get(binary_yes=False)

			current_price_yes = yes_option.price_set.get(is_last=True)
			current_price_no = no_option.price_set.get(is_last=True)

			print("Yes option is: " + yes_option.name + ", and no option is: " + no_option.name + ". Entring the atomic method...")
			overwrite_prices(current_price_yes, current_price_no)

		else:  #Non binary markets
			print("Market is not binary")
			for option in market.option_set.all():
				current_price_yes = option.price_set.get(is_last=True, is_yes=True)
				current_price_no = option.price_set.get(is_last=True, is_yes=False)

				print("Entring the atomic method for option " + option.name)
				overwrite_prices(current_price_yes, current_price_no)

	print("Register prices method finished.")

def overwrite_prices(current_price_yes, current_price_no):
	with transaction.atomic():
		print("In the transaction. Setting old prices is_last to False, and saving them...")
		#  Now the previous "last prices" are no longer the last prices.
		current_price_yes.is_last = False
		current_price_no.is_last = False
		current_price_yes.save()
		current_price_no.save()

		print("Current price yes: " + str(current_price_yes) + " and current price no: " + str(current_price_no))
		print("Going to create the new prices, copying the old ones and setting is_last to True.")
		#  Creation of 2 new prices, one for each option, that are the last prices.
		new_yes_price = Price.objects.create(option=current_price_yes.option, is_yes=True, is_last=True, buy_price=current_price_yes.buy_price)
		new_no_price = Price.objects.create(option=current_price_no.option, is_yes=False, is_last=True, buy_price=current_price_no.buy_price)

		print("Prices created. Yes price: " + new_yes_price + ". No price: " + str(new_no_price))
		print("Finishing transaction method...")


print("Scheduling tasks...")
scheduler.start()