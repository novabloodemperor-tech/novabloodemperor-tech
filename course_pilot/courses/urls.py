from django.urls import path
from . import views

urlpatterns = [
    path('check-eligibility/', views.check_eligibility, name='check_eligibility'),
]