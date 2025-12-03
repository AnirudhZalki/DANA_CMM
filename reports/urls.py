from django.urls import path
from .views import dashboard, verify_exit, delete_row

urlpatterns = [
    path('', dashboard, name='dashboard'),
    path("verify-exit/", verify_exit),
    path("delete-row/", delete_row, name="delete_row"),


]
