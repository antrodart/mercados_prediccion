from django import forms
from django.contrib.auth import authenticate
from django.contrib.auth.forms import UserCreationForm
from .admin import *
from .validators import validate_date_of_birth
from django.utils.translation import gettext_lazy as _
from mercados_de_prediccion_project import settings


class LoginForm(forms.Form):
	email = forms.EmailField(max_length=255, required=True)
	password = forms.CharField(widget=forms.PasswordInput, required=True)

	def clean(self):
		email = self.cleaned_data.get('email')
		password = self.cleaned_data.get('password')
		user = authenticate(email=email, password=password)
		if not user:
			raise forms.ValidationError(_("Sorry, that login was invalid. Please try again."))
		elif not user.is_active:
			raise forms.ValidationError(_("Sorry, that user was banned."))
		return self.cleaned_data

	def login(self, request):
		email = self.cleaned_data.get('email')
		password = self.cleaned_data.get('password')
		user = authenticate(email=email, password=password)
		return user


class SignupForm(UserCreationForm):
	first_name = forms.CharField(label=_("First name"), max_length=30, required=True, widget=forms.TextInput(attrs={}))
	last_name = forms.CharField(label=_("Last name"), max_length=60, required=True, widget=forms.TextInput(attrs={}))
	email = forms.EmailField(max_length=254, help_text='Required. Inform a valid email address.',
	                         widget=forms.EmailInput(attrs={'autofocus': None}))
	date_of_birth = forms.DateField(label=_("Birthdate"), widget=forms.DateInput,
	                              validators=[validate_date_of_birth])

	class Meta(UserCreationForm.Meta):
		model = CustomUser
		fields = ('first_name', 'last_name', 'date_of_birth', 'email', 'password1', 'password2',)


class EditProfileForm(forms.ModelForm):
	first_name = forms.CharField(label=_("First name"), max_length=30, required=True)
	last_name = forms.CharField(label=_("Last name"), max_length=60, required=True)
	date_of_birth = forms.DateField(label=_("Birth date"))

	class Meta:
		model = CustomUser
		fields = ('first_name', 'last_name', 'date_of_birth',)