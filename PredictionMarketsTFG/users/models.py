from django.db import models
from django.contrib.auth.models import AbstractUser, BaseUserManager
from mercados_de_prediccion_project.validators import validate_date_is_past
import json
import os

DEFAULT_USER_IMG = json.load(open(os.path.join(os.getcwd(), 'mercados_de_prediccion\static\img\default_user_img.json')))["data"]

class UserManager(BaseUserManager):
	"""Define a model manager for User model with no username field."""

	use_in_migrations = True

	def _create_user(self, email, password, **extra_fields):
		"""Create and save a User with the given email and password."""
		if not email:
			raise ValueError('The given email must be set')
		email = self.normalize_email(email)
		user = self.model(email=email, **extra_fields)
		user.set_password(password)
		user.save(using=self._db)
		return user

	def create_user(self, email, password=None, **extra_fields):
		"""Create and save a regular User with the given email and password."""
		extra_fields.setdefault('is_staff', False)
		extra_fields.setdefault('is_superuser', False)
		return self._create_user(email, password, **extra_fields)

	def create_superuser(self, email, password, **extra_fields):
		"""Create and save a SuperUser with the given email and password."""
		extra_fields.setdefault('is_staff', True)
		extra_fields.setdefault('is_superuser', True)

		if extra_fields.get('is_staff') is not True:
			raise ValueError('Superuser must have is_staff=True.')
		if extra_fields.get('is_superuser') is not True:
			raise ValueError('Superuser must have is_superuser=True.')

		return self._create_user(email, password, **extra_fields)


class User(AbstractUser):
	"""User model."""
	username = None
	email = models.EmailField(unique=True)
	date_of_birth = models.DateField(blank=True, null=True, validators=[validate_date_is_past])
	public_karma = models.IntegerField(null=False, default=0)
	picture = models.TextField(default=DEFAULT_USER_IMG)
	is_verified = models.BooleanField(null=False, default=False)

	USERNAME_FIELD = 'email'
	REQUIRED_FIELDS = []

	objects = UserManager()
