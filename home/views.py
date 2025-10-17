from django.contrib.gis.geos import Point
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from .zodb_store import open_db, commit
from .zo_models import (
    Home, Floor, Room,
    Lightbulb, Television, Fan, AirConditioner,
    add_home, add_floor, add_room, add_device,
    get_home, get_floor, get_room, get_device,
)
from .serializers import *
from .models import PositionHistory

open_db()  # ensure ZODB ready

# ---------- Home ----------
class HomeCreate(APIView):
    def post(self, request):
        ser = HomeCreateSer(data=request.data)
        ser.is_valid(raise_exception=True)
        h = Home(ser.validated_data["name"])
        add_home(h); commit()
        return Response({"id": h.id, "name": h.name}, status=201)

class HomeDetail(APIView):
    def get(self, request, home_id):
        h = get_home(home_id)
        if not h:
            return Response({"detail": "Not found"}, status=404)
        floors = [get_floor(fid) for fid in list(h.floor_ids)]    # <- cast
        return Response({
            "id": h.id,
            "name": h.name,
            "floors": [
                {
                    "id": f.id,
                    "level": f.level,
                    "rooms": [str(rid) for rid in list(f.room_ids)],  # <- cast
                }
                for f in floors
            ],
        })

# ---------- Floor ----------
class FloorCreate(APIView):
    def post(self, request, home_id):
        ser = FloorCreateSer(data=request.data)
        ser.is_valid(raise_exception=True)
        h = get_home(home_id)
        if not h: return Response({"detail":"Home not found"}, status=404)
        f = Floor(ser.validated_data["level"])
        add_floor(f, h.id); commit()
        return Response({"id": f.id, "level": f.level}, status=201)

class FloorRooms(APIView):
    def get(self, request, floor_id):
        f = get_floor(floor_id)
        if not f:
            return Response({"detail": "Not found"}, status=404)
        return Response({
            "id": f.id,
            "level": f.level,
            "rooms": [str(rid) for rid in list(f.room_ids)],   # <- cast
        })

# ---------- Room ----------
class RoomCreate(APIView):
    def post(self, request, floor_id):
        ser = RoomCreateSer(data=request.data)
        ser.is_valid(raise_exception=True)
        f = get_floor(floor_id)
        if not f: return Response({"detail":"Floor not found"}, status=404)
        r = Room(ser.validated_data["name"])
        add_room(r, f.id); commit()
        return Response({"id": r.id, "name": r.name}, status=201)

class RoomDevices(APIView):
    def get(self, request, room_id):
        r = get_room(room_id)
        if not r:
            return Response({"detail": "Not found"}, status=404)
        return Response({
            "room_id": r.id,
            "devices": [str(did) for did in list(r.device_ids)],
        })

# ---------- Device CRUD-ish ----------
class DeviceCreate(APIView):
    def post(self, request, room_id):
        ser = DeviceCreateSer(data=request.data)
        ser.is_valid(raise_exception=True)
        r = get_room(room_id)
        if not r: return Response({"detail":"Room not found"}, status=404)

        kwargs = dict(name=ser.validated_data["name"],
                      x=ser.validated_data["x"], y=ser.validated_data["y"], z=ser.validated_data["z"])
        t = ser.validated_data["type"]
        if t == "lightbulb": d = Lightbulb(**kwargs)
        elif t == "television": d = Television(**kwargs)
        elif t == "fan": d = Fan(**kwargs)
        else: d = AirConditioner(**kwargs)

        add_device(d, r.id); commit()
        return Response({"id": d.id, "type": d.type, "name": d.name}, status=201)

class DeviceDetail(APIView):
    def get(self, request, device_id):
        d = get_device(device_id)
        if not d: return Response({"detail":"Not found"}, status=404)
        base = {"id": d.id, "type": d.type, "name": d.name, "power": d.power, "position": [d.x,d.y,d.z]}
        if d.type == "lightbulb": base.update({"brightness": d.brightness, "colour": d.colour})
        if d.type == "television": base.update({"volume": d.volume, "channel": d.channel})
        if d.type == "fan": base.update({"speed": d.speed, "swing": d.swing})
        if d.type == "air_conditioner": base.update({"temperature": d.temperature})
        return Response(base)

# ---------- Device actions ----------
class DeviceTogglePower(APIView):
    def patch(self, request, device_id):
        d = get_device(device_id)
        if not d: return Response({"detail":"Not found"}, status=404)
        d.toggle_power(); commit()
        return Response({"id": d.id, "power": d.power})

class DeviceSetPosition(APIView):
    def patch(self, request, device_id):
        d = get_device(device_id)
        if not d: return Response({"detail":"Not found"}, status=404)
        ser = PositionSetSer(data=request.data)
        ser.is_valid(raise_exception=True)
        x,y,z = ser.validated_data["x"], ser.validated_data["y"], ser.validated_data["z"]

        # update ZODB
        d.set_position(x,y,z); commit()

        # record PostGIS history (lon=x, lat=y, z=z)
        PositionHistory.objects.create(
            device_id=d.id,
            point=Point(x, y, z)  # SRID 4326 by default
        )
        return Response({"id": d.id, "position": [d.x,d.y,d.z]})

class DeviceGetPosition(APIView):
    def get(self, request, device_id):
        d = get_device(device_id)
        if not d: return Response({"detail":"Not found"}, status=404)
        trail = PositionHistory.objects.filter(device_id=d.id).order_by("-recorded_at")[:100]
        history = [{"t": h.recorded_at.isoformat(), "x": h.point.x, "y": h.point.y, "z": h.point.z or 0.0}
                   for h in trail]
        return Response({"current": [d.x,d.y,d.z], "history": history})

# ---------- Type-specific PATCH ----------
class LightbulbPatch(APIView):
    def patch(self, request, device_id):
        d = get_device(device_id)
        if not d or d.type != "lightbulb": return Response({"detail":"Not found"}, status=404)
        ser = LightbulbPatchSer(data=request.data); ser.is_valid(raise_exception=True)
        for k,v in ser.validated_data.items(): setattr(d, k, v)
        commit(); return Response({"id": d.id, "brightness": d.brightness, "colour": d.colour})

class TelevisionPatch(APIView):
    def patch(self, request, device_id):
        d = get_device(device_id)
        if not d or d.type != "television": return Response({"detail":"Not found"}, status=404)
        ser = TelevisionPatchSer(data=request.data); ser.is_valid(raise_exception=True)
        for k,v in ser.validated_data.items(): setattr(d, k, v)
        commit(); return Response({"id": d.id, "volume": d.volume, "channel": d.channel})

class FanPatch(APIView):
    def patch(self, request, device_id):
        d = get_device(device_id)
        if not d or d.type != "fan": return Response({"detail":"Not found"}, status=404)
        ser = FanPatchSer(data=request.data); ser.is_valid(raise_exception=True)
        for k,v in ser.validated_data.items(): setattr(d, k, v)
        commit(); return Response({"id": d.id, "speed": d.speed, "swing": d.swing})

class AirConPatch(APIView):
    def patch(self, request, device_id):
        d = get_device(device_id)
        if not d or d.type != "air_conditioner": return Response({"detail":"Not found"}, status=404)
        ser = AirConPatchSer(data=request.data); ser.is_valid(raise_exception=True)
        for k,v in ser.validated_data.items(): setattr(d, k, v)
        commit(); return Response({"id": d.id, "temperature": d.temperature})
