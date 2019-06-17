from django.db import models
from django.db.models import Sum
from django.conf import settings
from django.core.validators import MaxValueValidator, MinValueValidator
from django.core.exceptions import ObjectDoesNotExist
from django.utils.translation import ugettext_lazy as _
from users.models import User
import datetime


class Category(models.Model):
	title = models.CharField(_('Title in English'), max_length=140, blank=False)
	title_es = models.CharField(_('Title in Spanish'), max_length=140, blank=False)
	picture = models.TextField(_('Picture'))


class Market(models.Model):
	title = models.CharField(max_length=150, blank=False)
	description = models.TextField(blank=False)
	end_date = models.DateField(null=False)
	creation_date = models.DateField(auto_now_add=True)
	picture = models.TextField()
	is_judged = models.BooleanField(default=False, null=False)
	is_binary = models.BooleanField(default=True, null=False)
	creator = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, null=False)
	categories = models.ManyToManyField(Category)
	group = models.ForeignKey('Group', on_delete=models.CASCADE, null=True)

	@property
	def has_expired(self):
		return self.end_date < datetime.date.today()

	def get_participants(self):
		participants = Asset.objects.filter(market_id=self.pk).aggregate(Sum('quantity'))
		print(participants)
		return participants

	def __str__(self):
		return self.title


class Option(models.Model):
	name = models.CharField(max_length=40, blank=False)
	is_correct = models.BooleanField(default=False, null=True)
	binary_yes = models.BooleanField(default=None, null=True)
	market = models.ForeignKey(Market, on_delete=models.CASCADE, null=False)

	def get_todays_price(self):
		if not self.market.is_binary:
			raise ObjectDoesNotExist(_("This method can only be used for binary market's options."))
		return self.price_set.get(is_last=True)

	def get_todays_price_yes(self):
		return self.price_set.get(is_yes=True, is_last=True)

	def get_todays_price_no(self):
		return self.price_set.get(is_yes=False, is_last=True)

	def get_todays_benefits(self):
		if not self.market.is_binary:
			raise ObjectDoesNotExist(_("This method can only be used for binary market's options."))
		return 100 - self.get_todays_price().buy_price

	def get_todays_benefits_yes(self):
		return 100 - self.get_todays_price_yes().buy_price

	def get_todays_benefits_no(self):
		return 100 - self.get_todays_price_no().buy_price


class Price(models.Model):
	buy_price = models.IntegerField(validators=[MaxValueValidator(99), MinValueValidator(1)], default=50)
	date = models.DateField(null=False, auto_now_add=True)
	is_yes = models.BooleanField(null=False)
	is_last = models.BooleanField(null=False, default=True)
	option = models.ForeignKey(Option, on_delete=models.CASCADE, null=False)


class Comment(models.Model):
	body = models.TextField(blank=False)
	rating = models.IntegerField(null=False, default=0)
	moment = models.DateTimeField(auto_now_add=True)
	market = models.ForeignKey(Market, on_delete=models.CASCADE, null=False)
	author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)


class Group(models.Model):
	name = models.CharField(max_length=70, blank=False)
	description = models.TextField(blank=False)
	picture = models.TextField(_('Picture'), blank=True, null=True)
	creation_date = models.DateTimeField(auto_now_add=True)
	is_visible = models.BooleanField(null=False, default=True)
	moderator = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, null=False)

	def descending_ordered_market_set(self):
		return self.market_set.order_by('-end_date')

	def descending_ordered_joinedgroup_karma_set(self):
		return self.joinedgroup_set.order_by('-private_karma')

	def joinedgroup_accepted_set(self):
		return self.joinedgroup_set.filter(is_accepted=True)

	def user_accepted_set(self):
		return self.joinedgroup_accepted_set().values_list('user', flat=True)

		#res = []
		#for joined_group in self.joinedgroup_accepted_set():
		#	res.append(joined_group.user)
		#return res


class JoinedGroup(models.Model):
	private_karma = models.IntegerField(null=False, default=0)
	joined_date = models.DateTimeField(auto_now_add=True)
	description = models.TextField(blank=True)
	is_accepted = models.BooleanField(null=False, default=False)
	user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, null=False)
	group = models.ForeignKey(Group, on_delete=models.CASCADE, null=False)


class Asset(models.Model):
	quantity = models.IntegerField(null=False, default=1)
	is_yes = models.BooleanField(null=False, default=True)
	has_expired = models.BooleanField(null=False, default=False)
	is_judged = models.BooleanField(null=False, default=False)
	user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, null=False)
	option = models.ForeignKey(Option, on_delete=models.CASCADE, null=False)
	market = models.ForeignKey(Market, on_delete=models.CASCADE, null=False)

