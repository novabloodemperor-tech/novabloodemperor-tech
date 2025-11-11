from django.http import HttpResponse
from django.urls import path, include
from django.contrib import admin

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('courses.urls')),
    path('', lambda request: HttpResponse("Backend is running!")),
]
