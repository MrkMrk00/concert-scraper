import json
from typing import Any
from enum import Enum
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

from scraper.models import Concert

DEFAULT_TZ = 'Europe/Prague'


class EventSerializer(json.JSONEncoder):
    def default(self, o: Any) -> Any:
        return { k:v for k, v in o.__dict__.items() 
                if v is not None and (type(v) != list or len(v) > 0) }


class RecurrenceRule:
    pass



@dataclass
class ReminderOverride:
    class Method(Enum):
        EMAIL = 'email'
        POPUP = 'popup'

    method: Method = Method.POPUP
    minutes: int = 30



@dataclass
class Reminders:
    useDefault: bool = True
    overrides: list[ReminderOverride] = field(default_factory=lambda: [])

    @classmethod
    def use_default(cls):
        return cls()



@dataclass
class EventTime:
    date: str|None = None
    dateTime: str|None = datetime.now(ZoneInfo(DEFAULT_TZ)).isoformat()
    timeZone: str|None = None

    @classmethod
    def from_datetime(cls, date_time: datetime, include_time: bool = True):
        if date_time.tzinfo is None:
            date_time = date_time.replace(tzinfo=ZoneInfo(DEFAULT_TZ))

        if include_time:
            return cls(dateTime=date_time.isoformat(), timeZone=date_time.tzname())

        return cls(
                date=date_time.strftime('%Y-%m-%d'),
                dateTime=None,
                timeZone=date_time.tzname(),
                )


@dataclass
class CalendarEvent:
    summary: str
    start: EventTime
    end: EventTime
    location: str|None = None
    description: str|None = None
    reminders: Reminders = field(default_factory=lambda: Reminders.use_default())
    extendedProperties: dict = field(default_factory=lambda: { 'private': { 'created_by': 'gcalconcertsync' } })

    def to_dict(self):
        return obj_to_dict(self)

    def to_json(self):
        return json.dumps(self, cls=EventSerializer)


    @classmethod
    def from_concert(cls, concert: Concert):
        return cls(
                summary=concert.name,
                location=concert.place,
                description=f'{concert.description}\nmeta: "gcalconcertsync"',
                start=EventTime.from_datetime(concert.start),
                end=EventTime.from_datetime(concert.end or (concert.start + timedelta(hours=2))),
                )


def obj_to_dict(val):
    ret = None

    try:
        ret = val.__dict__
        for k, v in ret.items():
            ret[k] = obj_to_dict(v)
    except AttributeError:
        ret = val

    return ret
