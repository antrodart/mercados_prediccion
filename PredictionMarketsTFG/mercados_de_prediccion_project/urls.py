"""mercados_de_prediccion_project URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import include, path
from django.conf.urls import url
from django.contrib.auth import views as auth_views
from users.views import signup, edit_profile, create_admin, login_view, change_password, verify_account, list_verify_requests, accept_verify_request, reject_verify_request, export_user_csv

urlpatterns = [
	path('admin/', admin.site.urls),
	path('login/', login_view, name="login"),
	path('logout/', auth_views.LogoutView.as_view(), name="logout"),
	path('signup/', signup, name="signup"),
	url(r'^auth/', include('social_django.urls', namespace='social')),
	path('user/edit/', edit_profile, name="edit_profile"),
	path('user/password/', change_password, name="change_password"),
	path('user/export', export_user_csv, name="export_user_csv"),
	path('verify/create/', verify_account, name='verify_account'),
	path('verify/list-requests/', list_verify_requests, name='list_verify_requests'),
	path('verify/accept/<int:verify_request_id>/', accept_verify_request, name='accept_verify_request'),
	path('verify/reject/<int:verify_request_id>/', reject_verify_request, name='reject_verify_request'),
	path('create-admin/', create_admin, name='create_admin'),
	path('', include('mercados_de_prediccion.urls')),
	url(r'^i18n/', include('django.conf.urls.i18n')),
	path('accounts/login/', login_view, name="login"),
	url(r'^password_reset/$', auth_views.PasswordResetView.as_view(), name='password_reset'),
	url(r'^password_reset/done/$', auth_views.PasswordResetDoneView.as_view(), name='password_reset_done'),
	url(r'^reset/(?P<uidb64>[0-9A-Za-z_\-]+)/(?P<token>[0-9A-Za-z]{1,13}-[0-9A-Za-z]{1,20})/$',
	    auth_views.PasswordResetConfirmView.as_view(), name='password_reset_confirm'),
	url(r'^reset/done/$', auth_views.PasswordResetCompleteView.as_view(), name='password_reset_complete'),
]

print("URLs imported.")
