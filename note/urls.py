from django.urls import path
from . import views


app_name = 'noteapp'

urlpatterns = [
    path('', views.IndexView.as_view(), name='index'),
    path('add/', views.AddView.as_view(), name='add'),
    path('note/<int:pk>/', views.SingleView.as_view(), name='single'),
    path('note/edit/<int:pk>/', views.EditView.as_view(), name='edit'),
    path('note/delete/<int:pk>/', views.Delete.as_view(), name='delete'),
    path('user/login/', views.UserLogin.as_view(), name='login'),
    path('user/logout/', views.UserLogout.as_view(), name='logout'),
    path('user/signup/', views.UserSignup.as_view(), name='signup'),
]
