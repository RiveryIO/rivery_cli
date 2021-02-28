import bson
import datetime
import uuid
import collections
import base64
from bson import ObjectId
import calendar
import decimal
import simplejson as json


def _datetime_to_millis(dtm):
    """Convert datetime to milliseconds since epoch UTC."""
    if dtm.utcoffset() is not None:
        dtm = dtm - dtm.utcoffset()
    return int(calendar.timegm(dtm.timetuple()) * 1000 +
               dtm.microsecond / 1000)


def object_hook(dct):
    if "$oid" in dct:
        return bson.ObjectId(str(dct["$oid"]))
    if "$date" in dct:
        dtm = dct["$date"]
        # mongoexport 2.6 and newer
        if isinstance(dtm, str):
            # Parse offset
            if dtm[-1] == 'Z':
                dt = dtm[:-1]
                offset = 'Z'
            elif dtm[-3] == ':':
                # (+|-)HH:MM
                dt = dtm[:-6]
                offset = dtm[-6:]
            elif dtm[-5] in ('+', '-'):
                # (+|-)HHMM
                dt = dtm[:-5]
                offset = dtm[-5:]
            elif dtm[-3] in ('+', '-'):
                # (+|-)HH
                dt = dtm[:-3]
                offset = dtm[-3:]
            else:
                dt = dtm
                offset = ''

            aware = datetime.datetime.strptime(
                dt, "%Y-%m-%dT%H:%M:%S.%f")

            if offset and offset != 'Z':
                if len(offset) == 6:
                    hours, minutes = offset[1:].split(':')
                    secs = (int(hours) * 3600 + int(minutes) * 60)
                elif len(offset) == 5:
                    secs = (int(offset[1:3]) * 3600 + int(offset[3:]) * 60)
                elif len(offset) == 3:
                    secs = int(offset[1:3]) * 3600
                if offset[0] == "-":
                    secs *= -1
                aware = aware - datetime.timedelta(seconds=secs)

            return aware.replace(tzinfo=None)
        # mongoexport 2.6 and newer, time before the epoch (SERVER-15275)
        elif isinstance(dtm, collections.Mapping):
            millis = int(dtm["$numberLong"])
        # mongoexport before 2.6
        else:
            millis = int(dtm)
        return millis

    if "$binary" in dct:
        if isinstance(dct["$type"], int):
            dct["$type"] = "%02x" % dct["$type"]
        subtype = int(dct["$type"], 16)
        if subtype >= 0xffffff80:  # Handle mongoexport values
            subtype = int(dct["$type"][6:], 16)
        data = base64.b64decode(dct["$binary"].encode())
        # special handling for UUID
        if subtype == uuid.UUID:
            return uuid.UUID(bytes=data)
        return bytes(data)
    if "$uuid" in dct:
        return uuid.UUID(dct["$uuid"])
    if "$undefined" in dct:
        return None
    return dct


def default(obj):
    # We preserve key order when rendering SON, DBRef, etc. as JSON by
    # returning a SON for those types instead of a dict.
    if isinstance(obj, ObjectId):
        return {"$oid": str(obj)}
    if isinstance(obj, datetime.datetime):
        millis = _datetime_to_millis(obj)
        return {"$date": millis}
    if isinstance(obj, bytes):
        return {'$binary', base64.b64encode(obj).decode()}

    if isinstance(obj, uuid.UUID):
        return {"$uuid": obj.hex}
    if isinstance(obj, decimal.Decimal):
        return {"$numberDecimal": str(obj)}


def loads(s, *args, **kwargs):
    """ Loads with object hook """
    return json.loads(s, object_hook=object_hook, *args, **kwargs)


def dumps(obj, *args, **kwargs):
    return json.dumps(obj, default=default, *args, **kwargs)


def convert_oid(s):
    try:
        return ObjectId(s)
    except Exception as e:
        return s