from .models import Concert, ConcertCollection
from .scraper import PageScraper
from datetime import datetime

def make_taboranka_concert(row: dict[str, str]) -> Concert|None:
    if row['Datum'] is None:
        return None

    date = row['Datum'].split(' ')[1].strip()
    time = row['Čas'] or '00:00'

    date_time = datetime.strptime(f'{date} {time}', '%d.%m.%y %H:%M')
    name = row['Akce']
    place = row['Místo']

    canceled = False
    if 'ZRUŠENO' in place:
        place = place.replace('ZRUŠENO', '').strip()
        canceled = True

    return Concert(name=name, place=place, date_time=date_time, canceled=canceled)

class TaborankaConcerts(PageScraper, ConcertCollection):
    URL = 'http://www.taboranka.cz/index.php?show=produkce'
    PAGE_ENC = 'latin-1'

    def __init__(self) -> None:
        super().__init__()
        self.init_page()

    def get_concerts(self) -> list[Concert]|None:
        concerts = []
        table = self.handle_table('.koncertytable', first_is_header=True)
        if table is None:
            return None

        for row in table:
            concert = make_taboranka_concert(row)
            if concert is not None:
                concerts.append(concert)

        return concerts

