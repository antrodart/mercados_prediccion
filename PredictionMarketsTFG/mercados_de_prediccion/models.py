from django.db import models
from django.conf import settings
from django.core.validators import MaxValueValidator, MinValueValidator
from django.utils.translation import ugettext_lazy as _
import datetime


class Category(models.Model):
	title = models.CharField(_('Title in English'), max_length=140, blank=False)
	title_es = models.CharField(_('Title in Spanish'), max_length=140, blank=False)
	picture = models.TextField(_('Picture'))


class Market(models.Model):
	title = models.CharField(max_length=280, blank=False)
	description = models.TextField(blank=False)
	end_date = models.DateField(null=False)
	picture = models.TextField()
	is_judged = models.BooleanField(default=False, null=False)
	creator = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, null=False)
	category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True)
	group = models.ForeignKey('Group', on_delete=models.CASCADE, null=True)

	@property
	def has_expired(self):
		return self.end_date < datetime.date.today()

	def __str__(self):
		return self.title


class Option(models.Model):
	title = models.CharField(max_length=140, blank=False)
	picture = models.TextField(blank=True)
	is_correct = models.BooleanField(default=None, null=True)
	market = models.ForeignKey(Market, on_delete=models.CASCADE, null=False)


class Price(models.Model):
	buy_price = models.IntegerField(validators=[MaxValueValidator(100), MinValueValidator(1)], default=50)
	sell_price = models.IntegerField(validators=[MaxValueValidator(100), MinValueValidator(1)], default=50)
	date = models.DateField(null=False)
	option = models.ForeignKey(Option, on_delete=models.CASCADE, null=False)


class Comment(models.Model):
	body = models.TextField(blank=False)
	rating = models.IntegerField(null=False, default=0)
	moment = models.DateTimeField(auto_now_add=True)
	market = models.ForeignKey(Market, on_delete=models.CASCADE, null=False)
	author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)


class Group(models.Model):
	name = models.CharField(max_length=140, blank=False)
	description = models.TextField(blank=False)
	picture = models.TextField(_('Picture'), blank=True, null=True)
	moderator = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, null=False)


class JoinedGroup(models.Model):
	private_karma = models.IntegerField(null=False, default=0)
	joined_date = models.DateTimeField(auto_now_add=True)
	description = models.TextField(blank=False)
	user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, null=False)
	group = models.ForeignKey(Group, on_delete=models.CASCADE, null=False)


class Asset(models.Model):
	has_expired = models.BooleanField(null=False, default=False)
	is_judged = models.BooleanField(null=False, default=False)
	user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, null=False)
	option = models.ForeignKey(Option, on_delete=models.CASCADE, null=False)

