from django.core.management.base import BaseCommand
from django.db import transaction
from django.db.models import F
from users.models import User
from mercados_de_prediccion.models import JoinedCommunity
import datetime

class Command(BaseCommand):
	help = 'This command gives 50 public and private Karma to every user.'

	def handle(self, *args, **kwargs):
		self.stdout.write("Trying to give the karma...")
		give_karma()


def give_karma():
	print("Getting users. Current time: " + str(datetime.datetime.now()))
	today = datetime.datetime.now()
	all_users = User.objects.all()

	with transaction.atomic():
		for user in all_users:
			print("Giving karma to: " + str(user))
			user.public_karma = F('public_karma') + 50
			user.save()
			accepted_joined_communities = JoinedCommunity.objects.filter(user=user, is_accepted=True)
			for joined_community in accepted_joined_communities:
				joined_community.private_karma = F('private_karma') + 50
				joined_community.save()

	print("Give karma method finished.")

