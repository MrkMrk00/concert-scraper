from gcalsync.sync import CalendarConnection
from gcalsync.objects import CalendarEvent, EventTime
from scraper.models import Concert, ConcertCollection
from scraper.taboranka import TaborankaConcerts 
from argparse import ArgumentParser, Namespace


CAL_ID = 'd89kmfjukmhij2ukvn4njl0ulo@group.calendar.google.com'

GROUPS: dict[str, type[ConcertCollection]] = {
    'taboranka': TaborankaConcerts,
}

def handle_print(args: Namespace):
    if args.what == 'cal':
        with CalendarConnection(CAL_ID) as c:
            if c is None:
                raise Exception('haha')

            res = c.list_events().execute()
            print(res)
        return

    if args.what == 'test_evt':
        evt = CalendarEvent(
                summary='Koncert',
                start=EventTime(),
                end=EventTime())

        print(evt.to_json())
        return

    concerts: list[Concert] = []
    
    for group in args.group:
        group_col = GROUPS.get(group)
        if group_col is None:
            continue

        concerts.extend(group_col().get_concerts() or [])

    for c in concerts or []:
        print(str(c))


def create_arg_parser() -> ArgumentParser:
    parser = ArgumentParser()
    
    subparsers = parser.add_subparsers(title='action', dest='action')

    print_parser = subparsers.add_parser('print', help='Prints fetched data into gcal (default)')
    print_parser.add_argument('what', choices=['cal', 'test_evt', 'scraped'], default='scraped')

    sync_parser = subparsers.add_parser('sync', help='Syncs fetched data into gcal')

    parser.add_argument('--group', choices=['taboranka'], default=['taboranka'], type=list)

    parser.set_defaults(action='print')
    return parser


def run(args):
    if args.action == 'print':
        handle_print(args)


if __name__ == '__main__':
    args = create_arg_parser().parse_args()
    run(args)

