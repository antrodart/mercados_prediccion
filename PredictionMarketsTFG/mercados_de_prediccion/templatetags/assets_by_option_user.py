from django import template
from django.db.models import Sum, Value
from django.db.models.functions import Coalesce
from django.utils.translation import ugettext as _
from django.core.exceptions import PermissionDenied
from mercados_de_prediccion.models import Asset

register = template.Library()


@register.simple_tag()
def get_assets_by_option_user(option, user):
	if not user.is_authenticated:
		raise PermissionDenied(_("You must be logged"))
	res = _("You don't have any assets yet.")
	assets = Asset.objects.filter(option=option, user=user).aggregate(quantity__sum=Coalesce(Sum('quantity'),Value(0)))['quantity__sum']
	if assets != 0:
		res = _("You have ")
		res += str(assets)
		res +=  _(" assets for this option")
	return res


@register.simple_tag()
def get_assets_user_bought_market_ended(option, user):
	if not user.is_authenticated:
		raise PermissionDenied(_("You must be logged"))
	res = _("You didn't buy any asset")
	assets = Asset.objects.filter(option=option, user=user).aggregate(quantity__sum=Coalesce(Sum('quantity'),Value(0)))['quantity__sum']
	if assets != 0:
		res = _("You bought ") + str(assets) + _(" assets")
	return res