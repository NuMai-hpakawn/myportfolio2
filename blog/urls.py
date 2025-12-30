from django.urls import path
from . import views

urlpatterns = [
    path('', views.post_list, name='post_list'),
    path('comment/<int:post_id>/', views.add_comment, name='add_comment'),
    path('analytics/', views.analytics, name='analytics'),
]

