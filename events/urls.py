from django.urls import path
from .views import event_detail_view

urlpatterns = [
    path("<int:pk>/", event_detail_view, name="event_detail"),
]