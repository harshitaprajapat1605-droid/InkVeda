from django.urls import path
from django.contrib.auth.views import LogoutView
from . import views

urlpatterns = [
    path('logout/', LogoutView.as_view(next_page='home'), name='logout'),
    path('dashboard/', views.dashboard, name='dashboard'), # Legacy/Hidden
    path('admin-dashboard/', views.admin_dashboard, name='admin_dashboard'),
]
