from django.urls import path
from . import views

urlpatterns = [
    path('', views.greenlight_view, name='greenlight'),
]
