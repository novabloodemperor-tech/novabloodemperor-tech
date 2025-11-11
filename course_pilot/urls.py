from django.http import HttpResponse
from django.urls import path, include
from django.contrib import admin

urlpatterns = [
    path('admin/', admin.site.urls),  # optional, if you use admin
    path('api/', include('courses.urls')),  # your API routes
    path('', lambda request: HttpResponse("Backend is running!")),  # root page
]

