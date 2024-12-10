from django.urls import path
from .views import login_view, verify_code

urlpatterns = [
    path('', login_view, name='login'),
    path('verify/', verify_code, name='verify'),
]
