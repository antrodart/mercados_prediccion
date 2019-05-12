from django.utils.translation import gettext_lazy as _
from django.utils.encoding import force_text
from django import forms
from .models import *
from .validators import validate_file_image_extension
import os
import json
import base64


class CreateCategoryForm(forms.ModelForm):
	title = forms.CharField(label=_('Title in English'), required=True, max_length=140)
	title_es = forms.CharField(label=_('Title in Spanish'), required=True, max_length=140)
	picture = forms.ImageField(label=_('Image'), validators=[validate_file_image_extension], required=True, help_text=_('Only .png and .jpg images format are accepted.'))

	class Meta():
		model = Category
		fields = ('title', 'title_es', 'picture',)

	def save(self, commit=True):
		category = super(CreateCategoryForm, self).save(commit=False)
		category.title = self.cleaned_data['title']
		category.title_es = self.cleaned_data['title_es']
		picture = self.cleaned_data['picture']
		if isinstance(picture, str):
			category.picture = picture
		else:
			encoded_picture = force_text(base64.b64encode(picture.file.read()))
			category.picture = encoded_picture
		if commit:
			category.save()
		return category


class CreateGroupForm(forms.ModelForm):
	name = forms.CharField(label=_('Name of the group'), required=True, max_length=140)
	description = forms.CharField(max_length=300, required=True,
	                              widget=forms.Textarea(attrs={'placeholder': _('Describe your group: rules, objectives and general information')}),
	                              label=_('Description'))
	picture = forms.ImageField(label=_('Image'), validators=[validate_file_image_extension], required=False,
	                           help_text=_('Only .png and .jpg images format are accepted.'))

	class Meta():
		model = Group
		fields = ('name', 'description', 'picture',)

	def __init__(self, *args, **kwargs):
		self.user = kwargs.pop('user')
		super(CreateGroupForm, self).__init__(*args, **kwargs)

	def save(self, commit=True):
		group = super(CreateGroupForm,self).save(commit=False)
		group.name = self.cleaned_data['name']
		group.description = self.cleaned_data['description']
		group.moderator = self.user
		picture = self.cleaned_data['picture']
		if not picture:
			group.picture = json.load(open(os.path.join(os.getcwd(), 'mercados_de_prediccion\static\img\default_group_img.json')))["data"]
		else:
			if isinstance(picture, str):
				group.picture = picture
			else:
				encoded_picture = force_text(base64.b64encode(picture.file.read()))
				group.picture = encoded_picture
		if commit:
			group.save()
		return group