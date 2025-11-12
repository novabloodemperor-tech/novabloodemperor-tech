from django.urls import path
from . import views

urlpatterns = [
    path('check-eligibility/', views.check_eligibility, name='check_eligibility'),
    path('pay/', views.pay, name='pay'),
    path('download-pdf/', views.download_courses_pdf, name='download_pdf'),
]
