from django.urls import path
from . import views

app_name = 'teacher_portal'

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('units/', views.unit_list, name='unit_list'),
    path('units/new/', views.unit_edit, name='unit_new'),
    path('units/<int:pk>/', views.unit_edit, name='unit_edit'),
    path('units/<int:pk>/delete/', views.unit_delete, name='unit_delete'),
    path('units/<int:pk>/clone/', views.unit_clone, name='unit_clone'),
    path('units/<int:pk>/print/', views.unit_print, name='unit_print'),
    path('calendar/', views.calendar_view, name='calendar'),
]
