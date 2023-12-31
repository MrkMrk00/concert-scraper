from dataclasses import dataclass
from datetime import datetime
from abc import ABCMeta, abstractmethod

@dataclass
class Concert:
    name: str
    start: datetime
    place: str
    end: datetime|None = None

    description: str = ''
    canceled: bool = False

    def format_date_time(self, format: str|None = None, include_year: bool = False):
        if format is None:
            if self.start.strftime('%H:%M') == '00:00':
                format = f'%d.%m{"%y" if include_year else ""}' 
            else:
                format = f'%d.%m{"%y" if include_year else ""} %H:%M'

        return self.start.strftime(format) + (
                f'- {self.end.strftime("%H:%M")}'
                if self.end is not None else ''
                )

    def __str__(self):
        str = ''
        if self.canceled:
            str += 'ZRUŠENO -- '

        str += f'{self.place} {self.format_date_time()}: '
        str += self.name

        return str



class ConcertCollection(metaclass=ABCMeta):
    @abstractmethod
    def get_concerts(self, *args, **kwargs) -> list[Concert]|None:
        pass

