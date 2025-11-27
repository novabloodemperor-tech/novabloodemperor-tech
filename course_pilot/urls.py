from django.http import HttpResponse
from django.urls import path, include
from django.contrib import admin

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('course_pilot.courses.urls')),
    path('version/', lambda request: HttpResponse("Version: Pay endpoint included - Latest")),  # ADD THIS
    path('', lambda request: HttpResponse("Backend is running!")),
]

