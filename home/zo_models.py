from abc import ABC, abstractmethod
from persistent import Persistent
from persistent.list import PersistentList
from .zodb_store import new_id, root

class Device(Persistent, ABC):
    """Abstract base class for all device types stored in ZODB."""
    def __init__(self, name, x=0.0, y=0.0, z=0.0, power=False):
        self.id = new_id()
        self.name = name
        self.power = bool(power)
        self.x = float(x)
        self.y = float(y)
        self.z = float(z)
        self.type = self.__class__.__name__.lower()

    def toggle_power(self):
        self.power = not self.power

    def set_position(self, x, y, z):
        self.x, self.y, self.z = float(x), float(y), float(z)

    @abstractmethod
    def status(self):
        """Each concrete device should implement a simple status dict."""
        pass


class Lightbulb(Device):
    def __init__(self, name, **kw):
        super().__init__(name, **kw)
        self.brightness = 100
        self.colour = "white"

    def status(self):
        return {"brightness": self.brightness, "colour": self.colour}


class Television(Device):
    def __init__(self, name, **kw):
        super().__init__(name, **kw)
        self.volume = 10
        self.channel = 1

    def status(self):
        return {"volume": self.volume, "channel": self.channel}


class Fan(Device):
    def __init__(self, name, **kw):
        super().__init__(name, **kw)
        self.speed = 1
        self.swing = False

    def status(self):
        return {"speed": self.speed, "swing": self.swing}


class AirConditioner(Device):
    def __init__(self, name, **kw):
        super().__init__(name, **kw)
        self.temperature = 24.0

    def status(self):
        return {"temperature": self.temperature}


class Room(Persistent):
    def __init__(self, name):
        self.id = new_id()
        self.name = name
        self.device_ids = PersistentList()


class Floor(Persistent):
    def __init__(self, level: int):
        self.id = new_id()
        self.level = int(level)
        self.room_ids = PersistentList()


class Home(Persistent):
    def __init__(self, name):
        self.id = new_id()
        self.name = name
        self.floor_ids = PersistentList()


# ------- helpers for indexing / relationships -------
def idx():
    return root()["indexes"]

def add_home(h: Home):
    idx()["homes"][h.id] = h

def add_floor(f: Floor, home_id: str):
    idx()["floors"][f.id] = f
    idx()["homes"][home_id].floor_ids.append(f.id)

def add_room(r: Room, floor_id: str):
    idx()["rooms"][r.id] = r
    idx()["floors"][floor_id].room_ids.append(r.id)

def add_device(d: Device, room_id: str):
    idx()["devices"][d.id] = d
    idx()["rooms"][room_id].device_ids.append(d.id)

def get_home(home_id): return idx()["homes"].get(home_id)
def get_floor(floor_id): return idx()["floors"].get(floor_id)
def get_room(room_id): return idx()["rooms"].get(room_id)
def get_device(device_id): return idx()["devices"].get(device_id)
