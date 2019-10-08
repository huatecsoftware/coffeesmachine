"""cafeServer URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.11/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
import os
from cafeClient import views
from django.conf.urls import url
from django.contrib import admin
from django.views.static import serve

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

urlpatterns = [
    url(r'^admin/', admin.site.urls),
    url(r'^PLCON/', views.PLCON, name='PLCON'),
    url(r'^PLCOFF/', views.PLCOFF, name='PLCOFF'),
    url(r'^logRcv/', views.logRcv, name='logRcv'),
    url(r'^loopDB/', views.loopDB, name='loopDB'),
    url(r'^addUser/', views.addUser, name='addUser'),
    url(r'^addCheck/', views.addCheck, name='addCheck'),
    url(r'^addOrder/', views.addOrder, name='addOrder'),
    url(r'^logClear/', views.logClear, name='logClear'),
    url(r'^failOrder/', views.failOrder, name='failOrder'),
    url(r'^rangeClick/', views.rangeClick, name='rangeClick'),
    url(r'^photograph/', views.photograph, name='photograph'),
    url(r'^calcFeature/', views.calcFeature, name='calcFeature'),
    url(r'^searchOrder/', views.searchOrder, name='searchOrder'),
    url(r'^queryAllOrder/', views.queryAllOrder, name='queryAllOrder'),
    url(r'^deleteTempFile/', views.deleteTempFile, name='deleteTempFile'),
    url(r'^intelligenceModel/', views.intelligenceModel, name='intelligenceModel'),
    url(r'^cafeBack/(?P<path>.*)$', serve,
        {'document_root': BASE_DIR+'/faces'}),
]
