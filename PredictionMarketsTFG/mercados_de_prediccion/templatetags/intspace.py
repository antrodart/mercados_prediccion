from django import template
import re

register = template.Library()


@register.simple_tag()
def intspace_dot(value):
	orig = str(value)
	new = re.sub(r"^(-?\d+)(\d{3})", r'\g<1>.\g<2>', orig)
	if orig == new:
		return new
	else:
		return intspace_dot(new)


@register.simple_tag()
def intspace_comma(value):
	orig = str(value)
	new = re.sub(r"^(-?\d+)(\d{3})", r'\g<1>,\g<2>', orig)
	if orig == new:
		return new
	else:
		return intspace_comma(new)
