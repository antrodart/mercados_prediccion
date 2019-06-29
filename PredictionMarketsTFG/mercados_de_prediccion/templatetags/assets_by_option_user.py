from django import template
from django.utils.translation import ugettext_lazy as _
from mercados_de_prediccion.models import Asset

register = template.Library()


@register.simple_tag()
def get_assets_by_option_user(option, user):
	res = _("You don't have any assets yet.")
	assets = Asset.objects.filter(option=option, user=user)
	if assets.exists():
		res = _("You have " + str(assets.first().quantity) + " assets for this option.")
	return res