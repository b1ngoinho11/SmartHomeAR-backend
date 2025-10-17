from django.urls import path
from .views import *

urlpatterns = [
    path("home/", HomeCreate.as_view()),
    path("home/<str:home_id>/", HomeDetail.as_view()),

    path("home/<str:home_id>/floors/", FloorCreate.as_view()),
    path("floors/<str:floor_id>/rooms/", FloorRooms.as_view()),

    path("floors/<str:floor_id>/rooms/create/", RoomCreate.as_view()),
    path("rooms/<str:room_id>/devices/", RoomDevices.as_view()),

    path("rooms/<str:room_id>/devices/create/", DeviceCreate.as_view()),
    path("devices/<str:device_id>/", DeviceDetail.as_view()),
    path("devices/<str:device_id>/toggle_power/", DeviceTogglePower.as_view()),
    path("devices/<str:device_id>/position/", DeviceGetPosition.as_view()),
    path("devices/<str:device_id>/position/set/", DeviceSetPosition.as_view()),

    path("devices/<str:device_id>/lightbulb/", LightbulbPatch.as_view()),
    path("devices/<str:device_id>/television/", TelevisionPatch.as_view()),
    path("devices/<str:device_id>/fan/", FanPatch.as_view()),
    path("devices/<str:device_id>/aircon/", AirConPatch.as_view()),
]
