from django.urls import path

from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('new', views.analysis_new, name='new'),
    path('<str:analysis_id>/upload', views.analysis_upload, name='upload'),
    path('<str:analysis_id>', views.analysis_show, name='show'),
]
