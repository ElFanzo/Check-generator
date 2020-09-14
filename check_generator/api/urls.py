from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^create_checks/', views.create_checks_view),
    url(r'^new_checks/', views.get_new_checks),
    url(r'^check/', views.get_check),
]
