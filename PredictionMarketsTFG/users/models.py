from django.db import models
from django.template.defaultfilters import slugify
from django.core.validators import MinValueValidator
from django.contrib.auth.models import AbstractUser, BaseUserManager
from mercados_de_prediccion_project.validators import validate_date_is_past


DEFAULT_USER_IMG = "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"

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
	first_name = models.CharField(max_length=30, blank=False)
	last_name = models.CharField(max_length=60, blank=False)
	email = models.EmailField(unique=True, max_length=150)
	date_of_birth = models.DateField(blank=True, null=True, validators=[validate_date_is_past])
	biography = models.TextField(blank=True, null=True)
	public_karma = models.IntegerField(null=False, default=500, validators=[MinValueValidator(0)])
	picture = models.TextField(default=DEFAULT_USER_IMG)
	is_verified = models.BooleanField(null=False, default=False)
	deletion_date = models.DateField(null=True, default=None)

	USERNAME_FIELD = 'email'
	REQUIRED_FIELDS = []

	objects = UserManager()

	def get_joined_community_accepted_set(self):
		return self.joinedcommunity_set.filter(is_accepted=True)

	def slug(self):
		return slugify(self.first_name + " " + self.last_name)
