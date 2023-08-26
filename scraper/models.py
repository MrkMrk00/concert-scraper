from dataclasses import dataclass
from datetime import datetime

@dataclass
class Concert:
    name: str
    date_time: datetime
    place: str

    description: str = ''
    canceled: bool = False

    def format_date_time(self, format: str|None = None, include_year: bool = False):
        if format is None:
            if self.date_time.strftime('%H:%M') == '00:00':
                format = f'%d.%m{"%y" if include_year else ""}' 
            else:
                format = f'%d.%m{"%y" if include_year else ""} %H:%M'

        return self.date_time.strftime(format)

    def __str__(self):
        str = ''
        if self.canceled:
            str += 'ZRUŠENO -- '

        str += f'{self.place} {self.format_date_time()}: '
        str += self.name

        return str
