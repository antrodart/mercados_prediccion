from django import forms
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from .models import CustomUser
from django.utils.translation import gettext_lazy as _
from mercados_de_prediccion_project import settings

class SignupForm(UserCreationForm):
	first_name = forms.CharField(label=_("First name"),max_length=30, required=True, widget=forms.TextInput(attrs={}))
	last_name = forms.CharField(label=_("Last name"),max_length=60, required=True, widget=forms.TextInput(attrs={}))
	birth_date = forms.DateField(label=_("Birth date"),widget=forms.DateInput(format=settings.DATE_INPUT_FORMATS), input_formats=settings.DATE_INPUT_FORMATS)
	email = forms.EmailField(max_length=254, help_text='Required. Inform a valid email address.', widget=forms.EmailInput(attrs={}))

	class Meta(UserCreationForm.Meta):
		model = CustomUser
		fields = ('first_name', 'last_name', 'birth_date', 'email', 'password1', 'password2', )
		#fields = UserCreationForm.Meta.fields


class EditProfileForm(forms.ModelForm):
	first_name = forms.CharField(label=_("First name"), max_length=30, required=True)
	last_name = forms.CharField(label=_("Last name"), max_length=60, required=True)
	birth_date = forms.DateField(label=_("Birth date"))

	class Meta:
		model = CustomUser
		fields = ('first_name', 'last_name', 'birth_date',)