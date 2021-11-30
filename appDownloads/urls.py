"""appDownloads URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.1/topics/http/urls/
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
# from django.contrib import admin
from django.urls import path

from appDownloads.views import index

urlpatterns = [
    #    path('admin/', admin.site.urls),
    path('', index.index, name='index'),
    path('app/<str:env>/<str:identifier>', index.app, name='app'),
    path('upload/<str:env>', index.upload, name='upload'),
    # path('<str:app>', index.app, name='index'),
]

# handler400 = err.bad_request
# handler403 = err.permission_denied
# handler404 = err.page_not_found
# handler500 = err.server_error
