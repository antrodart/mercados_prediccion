from .models import *

def user_is_member_of_group(user, group):
	joined_group = JoinedGroup.objects.get(user=user, group=group)
	return joined_group