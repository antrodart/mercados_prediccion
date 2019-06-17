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


class CreateCommunityForm(forms.ModelForm):
	name = forms.CharField(label=_('Community name'), required=True, max_length=70)
	description = forms.CharField(max_length=300, required=True,
	                              widget=forms.Textarea(attrs={'placeholder': _('Describe your community: rules, objectives and general information')}),
	                              label=_('Description'))
	picture = forms.ImageField(label=_('Image'), validators=[validate_file_image_extension], required=False,
	                           help_text=_('Only .png and .jpg images format are accepted.'))
	is_visible = forms.BooleanField(label=_('Visibility'), help_text=_('Visible communities can be seen by anyone.'), required=False)

	class Meta():
		model = Community
		fields = ('name', 'description', 'picture',)

	def __init__(self, *args, **kwargs):
		self.user = kwargs.pop('user')
		super(CreateCommunityForm, self).__init__(*args, **kwargs)

	def save(self, commit=True):
		community = super(CreateCommunityForm,self).save(commit=False)
		community.name = self.cleaned_data['name']
		community.description = self.cleaned_data['description']
		community.moderator = self.user
		picture = self.cleaned_data['picture']
		if not picture:
			community.picture = json.load(open(os.path.join(os.getcwd(), 'mercados_de_prediccion\static\img\default_community_img.json')))["data"]
		else:
			if isinstance(picture, str):
				community.picture = picture
			else:
				encoded_picture = force_text(base64.b64encode(picture.file.read()))
				community.picture = encoded_picture
		if commit:
			community.save()
		return community


class CategoryChoiceField(forms.ModelMultipleChoiceField):
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
	                           help_text=_("The date on which the market is finished and you can no longer bet. Must be format mm/dd/yyyy."),
	                            validators=[validate_date_is_future])
	picture = forms.ImageField(label=_('Image'), validators=[validate_file_image_extension], required=False,
	                           help_text=_('Only .png and .jpg images format are accepted.'))
	categories = CategoryChoiceField(label=_("Categories"), queryset=Category.objects.all(), required=False,)
	CHOICES = [(1, _('Binary')), (0, _('Multiple'))]
	is_binary = forms.ChoiceField(label=_("Type of market"), choices=CHOICES,
	                              widget=forms.RadioSelect(attrs={'id': 'value', 'class': 'custom-control-input'}),
	                              required=True, help_text=_('Binary markets only accept yes/no contract options. Multiple markets accept more than one predefined options.'))

	class Meta():
		model = Market
		fields = ('title', 'description', 'end_date', 'picture', 'categories', 'is_binary')

	def __init__(self, *args, **kwargs):
		self.user = kwargs.pop('user')
		self.community = kwargs.pop('community')
		super(CreateMarketForm, self).__init__(*args, **kwargs)

	def save(self, commit=True):
		market = super(CreateMarketForm,self).save(commit=False)
		market.title = self.cleaned_data['title']
		market.description = self.cleaned_data['description']
		market.end_date = self.cleaned_data['end_date']
		market.is_binary = self.cleaned_data['is_binary']
		market.creator = self.user
		market.community = self.community
		picture = self.cleaned_data['picture']
		if not picture:
			market.picture = json.load(open(os.path.join(os.getcwd(), 'mercados_de_prediccion\static\img\default_community_img.json')))["data"]
		else:
			if isinstance(picture, str):
				market.picture = picture
			else:
				encoded_picture = force_text(base64.b64encode(picture.file.read()))
				market.picture = encoded_picture
		if commit:
			market.save()
			market.categories.set(self.cleaned_data['categories'])
		return market


class EditMarketForm(forms.ModelForm):
	description = forms.CharField(required=True,
	                              widget=forms.Textarea(attrs={'placeholder': _(
		                              'It must contain all the possible information of the event to be predicted, so that no user has any doubt.')}),
	                              label=_('Description'))
	picture = forms.ImageField(label=_('Image'), validators=[validate_file_image_extension], required=False,
	                           help_text=_('Only .png and .jpg images format are accepted.'))
	categories = CategoryChoiceField(label=_("Category"), queryset=Category.objects.all(), required=False, )

	class Meta():
		model = Market
		fields = ('description', 'picture', 'categories',)

	def save(self, commit=True):
		market = super(EditMarketForm,self).save(commit=False)
		market.description = self.cleaned_data['description']
		market.categories.set(self.cleaned_data['categories'])
		picture = self.cleaned_data['picture']
		if not picture:
			market.picture = json.load(open(os.path.join(os.getcwd(), 'mercados_de_prediccion\static\img\default_community_img.json')))["data"]
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
	                        required=True, max_length=40)


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

				# Check that no two options have the same name
				if name in names:
					duplicates = True
				names.append(name)

				if duplicates:
					raise forms.ValidationError('Options must have unique names.', code='duplicate_names')


class MakeRequestToJoinForm(forms.ModelForm):
	description = forms.CharField(required=True,
	                              widget=forms.Textarea(attrs={'placeholder': _(
		                              'It must contain all the possible information to help the moderators decide to invite you.')}),
	                              label=_('Description'))

	class Meta():
		model = JoinedCommunity
		fields = ('description',)

	def __init__(self, *args, **kwargs):
		self.user = kwargs.pop('user')
		self.community = kwargs.pop('community')
		super(MakeRequestToJoinForm, self).__init__(*args, **kwargs)

	def save(self, commit=True):
		joined_community = super(MakeRequestToJoinForm, self).save(commit=False)
		joined_community.description = self.cleaned_data['description']
		joined_community.is_accepted = False
		joined_community.user = self.user
		joined_community.community = self.community

		if commit:
			joined_community.save()
		return joined_community


class CreateAssetForm(forms.ModelForm):
	#is_yes = forms.BooleanField(label=_("Buy yes or no"))
	quantity = forms.IntegerField(label=_("Quantity"), help_text=_('The quantity of assets you want to buy.'), required=True)
	class Meta():
		model = Asset
		fields = ('quantity',)

	def __init__(self, *args, **kwargs):
		self.user = kwargs.pop('user')
		self.market = kwargs.pop('market')
		super(CreateAssetForm, self).__init__(*args, **kwargs)

	def save(self, commit=True):
		asset = super(CreateAssetForm, self).save(commit=False)
		asset.quantity = self.cleaned_data['quantity']
		asset.has_expired = False
		asset.is_judged = False
		asset.market = self.market
		asset.user = self.user

		if commit:
			asset.save()
		return asset