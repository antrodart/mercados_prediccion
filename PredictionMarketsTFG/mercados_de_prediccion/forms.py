from django.utils.translation import gettext_lazy as _
from django.utils.encoding import force_text
from django import forms
from .models import *
from .validators import validate_file_image_extension
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
