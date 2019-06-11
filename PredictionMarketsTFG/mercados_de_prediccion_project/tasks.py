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


@scheduler.scheduled_job("cron", hour=0, minute=1, id="register_prices_per_day")
def register_prices_per_day():
	print("Registering prices")
	logging.info('Registering prices')
	today = datetime.datetime.now()
	markets_to_register_prices = Market.objects.filter(end_date__gte=today)  #Markets that haven't finished or finish today

	for market in markets_to_register_prices:
		if market.is_binary:  #  Binary markets
			yes_option = market.option_set.get(binary_yes=True)
			no_option = market.option_set.get(binary_yes=False)

			current_price_yes = yes_option.price_set.get(is_last=True)
			current_price_no = no_option.price_set.get(is_last=True)

			overwrite_prices(current_price_yes, current_price_no)

		else:  #Non binary markets
			for option in market.option_set.all():
				current_price_yes = option.price_set.get(is_last=True, is_yes=True)
				current_price_no = option.price_set.get(is_last=True, is_yes=False)

				overwrite_prices(current_price_yes, current_price_no)

	logging.info('Prices registered succesfully')

def overwrite_prices(current_price_yes, current_price_no):
	with transaction.atomic():
		#  Now the previous "last prices" are no longer the last prices.
		current_price_yes.is_last = False
		current_price_no.is_last = False
		current_price_yes.save()
		current_price_no.save()

		#  Creation of 2 new prices, one for each option, that are the last prices.
		Price.objects.create(option=current_price_yes.option, is_yes=True, is_last=True, buy_price=current_price_yes.buy_price)
		Price.objects.create(option=current_price_no.option, is_yes=False, is_last=True, buy_price=current_price_no.buy_price)
