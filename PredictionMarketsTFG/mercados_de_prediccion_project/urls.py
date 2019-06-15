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
from django.urls import include,path
from django.conf.urls import url
from django.contrib.auth import views as auth_views
from users.views import signup, edit_profile, create_admin, login_view

urlpatterns = [
    path('admin/', admin.site.urls),
    path('login/', login_view, name="login"),
	path('logout/', auth_views.LogoutView.as_view(), name="logout"),
	path('signup/', signup, name="signup"),
	path('user/edit/', edit_profile, name="edit_profile"),
	path('create-admin/', create_admin, name='create_admin'),
    path('',include('mercados_de_prediccion.urls')),
	url(r'^i18n/', include('django.conf.urls.i18n')),
	path('accounts/login/', login_view, name="login"),
]

print("URLs imported.")

