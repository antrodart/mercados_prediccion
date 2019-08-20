from django import forms
from django.utils.encoding import force_text
from django.contrib.auth import authenticate
from django.contrib.auth.forms import UserCreationForm
from django.utils.translation import gettext_lazy as _
from .models import User, VerifyRequest
from mercados_de_prediccion_project.validators import validate_date_is_past, validate_file_image_extension
from mercados_de_prediccion_project import default_pictures
import json
import base64
import os


class LoginForm(forms.Form):
	email = forms.EmailField(max_length=150, required=True)
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


class VerifyForm(forms.ModelForm):
	institution = forms.CharField(label=_("Institution"), max_length=60, required=True, )
	description = forms.CharField(max_length=300, required=True, label=_('Description'),
	                              widget=forms.Textarea(attrs={'placeholder': _(
		                              'Describe the institution you represent, and give us proofs that you are who you say you are. You can reference any email sent to predictmarket.us@gmail.com')}), )

	class Meta():
		model = VerifyRequest
		fields = ('institution', 'description',)

	def __init__(self, *args, **kwargs):
		self.user = kwargs.pop('user')
		self.old_verify_request = kwargs.pop('old_verify_request')
		super(VerifyForm, self).__init__(*args, **kwargs)

	def save(self, commit=True):
		if self.old_verify_request:
			verify_request = self.old_verify_request
			verify_request.is_accepted = None
		else:
			verify_request = super(VerifyForm, self).save(commit=False)
			verify_request.user = self.user
		verify_request.institution = self.cleaned_data['institution']
		verify_request.description = self.cleaned_data['description']
		if commit:
			verify_request.save()
		return verify_request

class SignupForm(UserCreationForm):
	first_name = forms.CharField(label=_("First name"), max_length=30, required=True, widget=forms.TextInput(attrs={}))
	last_name = forms.CharField(label=_("Last name"), max_length=60, required=True, widget=forms.TextInput(attrs={}))
	alias = forms.CharField(label=_("Alias"), help_text=_("The nickname by which they will know you."),
	                        max_length=30, required=True, widget=forms.TextInput(attrs={}))
	email = forms.EmailField(max_length=254, help_text='Required. Inform a valid email address.',
	                         widget=forms.EmailInput(attrs={'autofocus': None}))
	biography = forms.CharField(max_length=300, required=False,
	                            widget=forms.Textarea(attrs={'placeholder': _(
		                            'Describe yourself: your hobbies, life goals, preferences, interests...')}),
	                            label=_('Biography'))
	date_of_birth = forms.DateField(label=_("Date of birth"), widget=forms.DateInput, required=False,
	                                validators=[validate_date_is_past])
	picture = forms.ImageField(label=_('Picture'), validators=[validate_file_image_extension], required=False,
	                           help_text=_('Only .png and .jpg images format are accepted.'))

	class Meta(UserCreationForm.Meta):
		model = User
		fields = (
		'first_name', 'last_name', 'alias', 'date_of_birth', 'email', 'biography', 'picture', 'password1', 'password2',)

	def save(self, commit=True):
		user = super(SignupForm, self).save(commit=False)
		user.first_name = self.cleaned_data['first_name']
		user.last_name = self.cleaned_data['last_name']
		user.email = self.cleaned_data['email']
		user.biography = self.cleaned_data['biography']
		user.date_of_birth = self.cleaned_data['date_of_birth']
		picture = self.cleaned_data['picture']
		if not picture:
			user.picture = default_pictures.DEFAULT_USER_PICTURE
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
	alias = forms.CharField(label=_("Alias"), help_text=_("The nickname by which they will know you."),
	                        max_length=30, required=True)
	date_of_birth = forms.DateField(label=_("Date of birth"))
	biography = forms.CharField(max_length=300, required=False,
	                            widget=forms.Textarea(attrs={'placeholder': _(
		                            'Describe yourself: your hobbies, life goals, preferences, interests...')}),
	                            label=_('Biography'))
	picture = forms.ImageField(label=_('Picture'), validators=[validate_file_image_extension], required=False,
	                           help_text=_('Only .png and .jpg images format are accepted.'))

	class Meta:
		model = User
		fields = ('first_name', 'last_name', 'alias', 'biography', 'date_of_birth', 'picture',)

	def save(self, commit=True):
		user = super(EditProfileForm, self).save(commit=False)
		user.first_name = self.cleaned_data['first_name']
		user.last_name = self.cleaned_data['last_name']
		user.date_of_birth = self.cleaned_data['date_of_birth']
		user.biography = self.cleaned_data['biography']
		picture = self.cleaned_data['picture']

		if isinstance(picture, str):
			user.picture = picture
		else:
			encoded_picture = force_text(base64.b64encode(picture.file.read()))
			user.picture = encoded_picture
		if commit:
			user.save()
		return user
