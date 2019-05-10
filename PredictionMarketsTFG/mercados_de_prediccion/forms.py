from django.utils.translation import gettext_lazy as _
from django.utils.encoding import force_text
from django import forms
from .models import *
from .validators import validate_file_image_extension


class CreateCategoryForm(forms.Form):
	title = forms.CharField(label=_('Title'), required=True, max_length=140)
	picture = forms.ImageField(label=_('Image'), validators=[validate_file_image_extension], required=True, help_text=_('Only .png and .jpg images format are accepted.'))

	def save(self, encoded_picture):
		category = Category()
		category.title = self.cleaned_data['title']
		category.picture = force_text(encoded_picture)

		category.save()
		return category
