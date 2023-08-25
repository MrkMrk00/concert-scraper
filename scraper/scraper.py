from requests import get
from lxml import html
from datetime import datetime
from dataclasses import dataclass
from typing import Self


class InvalidPageException(Exception):
    pass


class PageScraper:
    URL: str = ''

    def __init__(self):
        (page_str, page) = self.parse_page(self.URL)

        self._page_str = page_str
        self._page = page


    def parse_page(self, url: str) -> tuple[str, html.HtmlElement]:
        page_str = get(url)
        if page_str is None:
            raise InvalidPageException('Page was not found')

        page_str = page_str.text
        page_str = page_str.encode('latin-1').decode('utf-8')

        page: html.HtmlElement = html.fromstring(page_str.encode())
        if page is None:
            raise InvalidPageException('Invalid page')

        return (page_str, page)


    def handle_table(self, selector: str, first_is_header: bool = False) -> list|None:
        form = self._page.cssselect(selector)
        if form is None or len(form) < 1:
            return None

        form: html.HtmlElement = form[0]
        header = None
        rows = []

        row_cnt = 0
        for tr in form.cssselect('tr'):
            tr: html.HtmlElement
            row = []
            
            for td in tr.cssselect('td'):
                td: html.HtmlElement
                text = td.text
                row.append(text)

            if first_is_header and row_cnt == 0:
                header = row
                row_cnt += 1
                continue

            if len(row) > 1:
                rows.append(row)
                row_cnt += 1

        if header is not None and first_is_header:
            values = rows
            rows = []
            for row in values:
                rows.append({ k:v for k, v in zip(header, row) })
                
        return rows


@dataclass
class Concert:
    name: str
    date_time: datetime
    place: str
    canceled: bool = False

    @classmethod
    def from_table_row(cls, row: dict[str, str]) -> Self|None:
        if row['Datum'] is None:
            return None

        date = row['Datum'].split(' ')[1].strip()
        time = row['Čas'] or '00:00'

        date_time = datetime.strptime(f'{date} {time}', '%d.%m.%y %H:%M')
        name = row['Akce']
        place = row['Místo']

        canceled = False
        if 'ZRUŠENO' in place:
            canceled = True

        return cls(name=name, place=place, date_time=date_time, canceled=canceled)

    def __str__(self):
         return f'{"ZRUŠENO -- " if self.canceled else ""}{self.date_time.strftime("%d.%m %H:%M")} {self.place}: {self.name}'


class Concerts(PageScraper):
    URL = 'http://www.taboranka.cz/index.php?show=produkce'

    def get_concerts(self) -> list[Concert]|None:
        concerts = []
        table = self.handle_table('.koncertytable', first_is_header=True)
        if table is None:
            return None

        for row in table:
            concert = Concert.from_table_row(row)
            if concert is not None:
                concerts.append(concert)

        return concerts



if __name__ == '__main__':
    concert_scraper = Concerts()
    for c in concert_scraper.get_concerts() or []:
        print(str(c))
