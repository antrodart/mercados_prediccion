from django import forms
from django.utils.encoding import force_text
from django.contrib.auth import authenticate
from django.contrib.auth.forms import UserCreationForm
from django.utils.translation import gettext_lazy as _
from .models import User
from mercados_de_prediccion_project.validators import validate_date_is_past, validate_file_image_extension
import json
import base64
import os


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
	date_of_birth = forms.DateField(label=_("Date of birth"), widget=forms.DateInput,
	                              validators=[validate_date_is_past])
	picture = forms.ImageField(label=_('Image'), validators=[validate_file_image_extension], required=False,
	                           help_text=_('Only .png and .jpg images format are accepted.'))

	class Meta(UserCreationForm.Meta):
		model = User
		fields = ('first_name', 'last_name', 'date_of_birth', 'email', 'picture', 'password1', 'password2',)

	def save(self, commit=True):
		user = super(SignupForm, self).save(commit=False)
		user.first_name = self.cleaned_data['first_name']
		user.last_name = self.cleaned_data['last_name']
		user.email = self.cleaned_data['email']
		user.date_of_birth = self.cleaned_data['date_of_birth']
		picture = self.cleaned_data['picture']
		if not picture:
			user.picture = json.load(open(os.path.join(os.getcwd(), 'mercados_de_prediccion\static\img\default_user_img.json')))["data"]
		else:
			if isinstance(picture, str):
				user.picture = picture
			else:
				encoded_picture = force_text(base64.b64encode(picture.file.read()))
				user.picture = encoded_picture
		if commit:
			user.save()
		return user


class EditProfileForm(forms.ModelForm):
	first_name = forms.CharField(label=_("First name"), max_length=30, required=True)
	last_name = forms.CharField(label=_("Last name"), max_length=60, required=True)
	date_of_birth = forms.DateField(label=_("Birth date"))
	picture = forms.ImageField(label=_('Image'), validators=[validate_file_image_extension], required=False,
	                           help_text=_('Only .png and .jpg images format are accepted.'))

	class Meta:
		model = User
		fields = ('first_name', 'last_name', 'date_of_birth', 'picture',)

	def save(self, commit=True):
		user = super(EditProfileForm, self).save(commit=False)
		user.first_name = self.cleaned_data['first_name']
		user.last_name = self.cleaned_data['last_name']
		user.date_of_birth = self.cleaned_data['date_of_birth']
		picture = self.cleaned_data['picture']

		if isinstance(picture, str):
			user.picture = picture
		else:
			encoded_picture = force_text(base64.b64encode(picture.file.read()))
			user.picture = encoded_picture
		if commit:
			user.save()
		return user
