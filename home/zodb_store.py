import os
import uuid
import transaction
from ZODB import FileStorage, DB
from persistent.mapping import PersistentMapping
from django.conf import settings

_db = None
_conn = None
_root = None

def open_db():
    global _db, _conn, _root
    if _db is None:
        os.makedirs(os.path.dirname(settings.ZODB_FILE), exist_ok=True)
        storage = FileStorage.FileStorage(str(settings.ZODB_FILE))
        _db = DB(storage)
        _conn = _db.open()
        _root = _conn.root()
        if "indexes" not in _root:
            _root["indexes"] = PersistentMapping()
        idx = _root["indexes"]
        for key in ("homes", "floors", "rooms", "devices"):
            if key not in idx:
                idx[key] = PersistentMapping()
        transaction.commit()
    return _db, _conn, _root

def root():
    if _root is None:
        open_db()
    return _root

def commit():
    transaction.commit()

def new_id() -> str:
    return str(uuid.uuid4())
