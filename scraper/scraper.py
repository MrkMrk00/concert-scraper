from requests import get
from lxml import html


class InvalidPageException(Exception):
    pass


class PageScraper:
    URL: str = ''
    PAGE_ENC: str = 'utf-8'

    def init_page(self) -> None:
        page_str, page = self.parse_page(self.URL)

        self._page_str = page_str
        self._page = page


    def parse_page(self, url: str) -> tuple[str, html.HtmlElement]:
        page_str = get(url)
        if page_str is None:
            raise InvalidPageException('Page was not found')

        page_str = page_str.text
        if self.PAGE_ENC != 'utf-8':
            page_str = page_str.encode(self.PAGE_ENC).decode('utf-8')

        page: html.HtmlElement = html.fromstring(page_str.encode())
        if page is None:
            raise InvalidPageException('Invalid page')

        return page_str, page


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



