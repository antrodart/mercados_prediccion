from apscheduler.schedulers.background import BackgroundScheduler
from users.models import User
import datetime


scheduler = BackgroundScheduler()


@scheduler.scheduled_job("cron", hour=0, minute=1, id="delete_users_marked")
def delete_users_marked():
	print("Deleting users")
	today = datetime.datetime.now()
	users_marked_deletion = User.objects.filter(deletion_date=today)

	for user in users_marked_deletion:
		print("Deleting user " + user.__str__())
		user.delete()


scheduler.start()
