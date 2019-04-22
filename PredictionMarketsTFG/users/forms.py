from django import forms
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from .models import CustomUser
from django.utils.translation import gettext_lazy as _

class SignupForm(UserCreationForm):
	first_name = forms.CharField(label=_("First name"),max_length=30, required=True)
	last_name = forms.CharField(label=_("Last name"),max_length=60, required=True)
	birth_date = forms.DateField(label=_("Birth date"))
	email = forms.EmailField(max_length=254, help_text='Required. Inform a valid email address.')

	class Meta(UserCreationForm.Meta):
		model = CustomUser
		fields = ('username', 'first_name', 'last_name', 'birth_date', 'email', 'password1', 'password2', )
		#fields = UserCreationForm.Meta.fields


class EditProfileForm(forms.Form):
	first_name = forms.CharField(label=_("First name"), max_length=30, required=True)
	last_name = forms.CharField(label=_("Last name"), max_length=60, required=True)
	birth_date = forms.DateField(label=_("Birth date"))

	class Meta:
		model = CustomUser
		fields = ('first_name', 'last_name', 'birth_date',)