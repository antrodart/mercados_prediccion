from django.utils.translation import gettext_lazy as _, get_language
from django.utils.encoding import force_text
from django import forms
from django.forms.formsets import BaseFormSet
from .models import *
from mercados_de_prediccion_project.validators import validate_file_image_extension, validate_date_is_future
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
	name = forms.CharField(label=_('Group name'), required=True, max_length=70)
	description = forms.CharField(max_length=300, required=True,
	                              widget=forms.Textarea(attrs={'placeholder': _('Describe your group: rules, objectives and general information')}),
	                              label=_('Description'))
	picture = forms.ImageField(label=_('Image'), validators=[validate_file_image_extension], required=False,
	                           help_text=_('Only .png and .jpg images format are accepted.'))
	is_visible = forms.BooleanField(label=_('Visible'), help_text=_('Visible groups can be seen by anyone.'), required=False)

	class Meta():
		model = Group
		fields = ('name', 'description', 'picture','is_visible',)

	def __init__(self, *args, **kwargs):
		self.user = kwargs.pop('user')
		super(CreateGroupForm, self).__init__(*args, **kwargs)

	def save(self, commit=True):
		group = super(CreateGroupForm,self).save(commit=False)
		group.name = self.cleaned_data['name']
		group.description = self.cleaned_data['description']
		group.is_visible = self.cleaned_data['is_visible']
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


class CategoryChoiceField(forms.ModelChoiceField):
	def label_from_instance(self, obj):
		if get_language() == "en":
			return str(obj.title)
		else:
			return str(obj.title_es)
	def widget_attrs(self, widget):
		return {'class':'custom-select',}


class CreateMarketForm(forms.ModelForm):
	title = forms.CharField(label=_('Title'),
	                        help_text=_('The title should briefly describe the event and the end date.'),
	                        required=True, max_length=150)
	description = forms.CharField(required=True,
	                              widget=forms.Textarea(attrs={'placeholder': _('It must contain all the possible information of the event to be predicted, so that no user has any doubt.')}),
	                              label=_('Description'))
	end_date = forms.DateField(label=_("End date"), widget=forms.DateInput, required=True,
	                           help_text=_("The date on which the market is finished and you can no longer bet."),
	                            validators=[validate_date_is_future])
	picture = forms.ImageField(label=_('Image'), validators=[validate_file_image_extension], required=False,
	                           help_text=_('Only .png and .jpg images format are accepted.'))
	category = CategoryChoiceField(label=_("Category"), queryset=Category.objects.all(), required=False,)
	CHOICES = [(1, _('Binary')), (0, _('Multiple'))]
	is_binary = forms.ChoiceField(label=_("Type of market"), choices=CHOICES,
	                              widget=forms.RadioSelect(attrs={'id': 'value', 'class': 'custom-control-input'}),
	                              required=True, help_text=_('Binary markets only accept yes/no contract options. Multiple markets accept more than one predefined options.'))

	class Meta():
		model = Market
		fields = ('title', 'description', 'end_date', 'picture', 'category', 'is_binary')

	def __init__(self, *args, **kwargs):
		self.user = kwargs.pop('user')
		self.group = kwargs.pop('group')
		super(CreateMarketForm, self).__init__(*args, **kwargs)

	def save(self, commit=True):
		market = super(CreateMarketForm,self).save(commit=False)
		market.title = self.cleaned_data['title']
		market.description = self.cleaned_data['description']
		market.end_date = self.cleaned_data['end_date']
		market.category = self.cleaned_data['category']
		market.is_binary = self.cleaned_data['is_binary']
		market.creator = self.user
		market.group = self.group
		picture = self.cleaned_data['picture']
		if not picture:
			market.picture = json.load(open(os.path.join(os.getcwd(), 'mercados_de_prediccion\static\img\default_group_img.json')))["data"]
		else:
			if isinstance(picture, str):
				market.picture = picture
			else:
				encoded_picture = force_text(base64.b64encode(picture.file.read()))
				market.picture = encoded_picture
		if commit:
			market.save()
		return market


class EditMarketForm(forms.ModelForm):
	description = forms.CharField(required=True,
	                              widget=forms.Textarea(attrs={'placeholder': _(
		                              'It must contain all the possible information of the event to be predicted, so that no user has any doubt.')}),
	                              label=_('Description'))
	picture = forms.ImageField(label=_('Image'), validators=[validate_file_image_extension], required=False,
	                           help_text=_('Only .png and .jpg images format are accepted.'))
	category = CategoryChoiceField(label=_("Category"), queryset=Category.objects.all(), required=False, )

	class Meta():
		model = Market
		fields = ('description', 'picture', 'category',)

	def save(self, commit=True):
		market = super(EditMarketForm,self).save(commit=False)
		market.description = self.cleaned_data['description']
		market.category = self.cleaned_data['category']
		picture = self.cleaned_data['picture']
		if not picture:
			market.picture = json.load(open(os.path.join(os.getcwd(), 'mercados_de_prediccion\static\img\default_group_img.json')))["data"]
		else:
			if isinstance(picture, str):
				market.picture = picture
			else:
				encoded_picture = force_text(base64.b64encode(picture.file.read()))
				market.picture = encoded_picture
		if commit:
			market.save()
		return market


class CreateOptionForm(forms.Form):
	"""
	    Form for individual options
	    """
	name = forms.CharField(label=_('Option'),
	                        help_text=_('The option that participants can bet on'),
	                        required=False, max_length=150)


class BaseOptionFormSet(BaseFormSet):
    def clean(self):
        """
        Adds validation to check that no two options have the same name
        """
        if any(self.errors):
            return

        names = []
        duplicates = False

        for form in self.forms:
            if form.cleaned_data:
                name = form.cleaned_data['name']
                image = form.cleaned_data['image']

                # Check that no two options have the same name
                if name in names:
                    duplicates = True
                names.append(name)

                if duplicates:
                    raise forms.ValidationError(
                        'Options must have unique names.',
                        code='duplicate_names'
                    )




class MakeRequestToJoinForm(forms.ModelForm):
	description = forms.CharField(required=True,
	                              widget=forms.Textarea(attrs={'placeholder': _(
		                              'It must contain all the possible information to help the moderators decide to invite you.')}),
	                              label=_('Description'))

	class Meta():
		model = JoinedGroup
		fields = ('description',)

	def __init__(self, *args, **kwargs):
		self.user = kwargs.pop('user')
		self.group = kwargs.pop('group')
		super(MakeRequestToJoinForm, self).__init__(*args, **kwargs)

	def save(self, commit=True):
		joined_group = super(MakeRequestToJoinForm, self).save(commit=False)
		joined_group.description = self.cleaned_data['description']
		joined_group.is_accepted = False
		joined_group.user = self.user
		joined_group.group = self.group

		if commit:
			joined_group.save()
		return joined_group