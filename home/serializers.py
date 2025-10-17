from rest_framework import serializers

class HomeCreateSer(serializers.Serializer):
    name = serializers.CharField()

class FloorCreateSer(serializers.Serializer):
    level = serializers.IntegerField()

class RoomCreateSer(serializers.Serializer):
    name = serializers.CharField()

class DeviceCreateSer(serializers.Serializer):
    name = serializers.CharField()
    type = serializers.ChoiceField(choices=["lightbulb","television","fan","air_conditioner"])
    x = serializers.FloatField(required=False, default=0.0)
    y = serializers.FloatField(required=False, default=0.0)
    z = serializers.FloatField(required=False, default=0.0)

class PositionSetSer(serializers.Serializer):
    x = serializers.FloatField()
    y = serializers.FloatField()
    z = serializers.FloatField()

class LightbulbPatchSer(serializers.Serializer):
    brightness = serializers.IntegerField(min_value=0, max_value=100, required=False)
    colour = serializers.CharField(required=False)

class TelevisionPatchSer(serializers.Serializer):
    volume = serializers.IntegerField(min_value=0, max_value=100, required=False)
    channel = serializers.IntegerField(min_value=1, required=False)

class FanPatchSer(serializers.Serializer):
    speed = serializers.IntegerField(min_value=0, max_value=5, required=False)
    swing = serializers.BooleanField(required=False)

class AirConPatchSer(serializers.Serializer):
    temperature = serializers.FloatField(required=False)
