from gcalsync.objects import CalendarEvent
from gcalsync.sync import CalendarConnection, Synchronizer
from scraper.models import Concert, ConcertCollection
from scraper.taboranka import TaborankaConcerts 
from argparse import ArgumentParser, Namespace, BooleanOptionalAction


GROUPS: dict[str, type[ConcertCollection]] = {
    'taboranka': TaborankaConcerts,
}


def handle_print(args: Namespace):
    concerts: list = []
    
    for group in args.group:
        group_col = GROUPS.get(group)
        if group_col is None:
            continue

        concerts.extend(group_col().get_concerts() or [])

    concerts = concerts or []
    if args.as_events:
        concerts = [ CalendarEvent.from_concert(c) for c in concerts ]

    for c in concerts or []:
        if type(c) == CalendarEvent:
            print(c.to_json())
        else:
            print(str(c))

def handle_sync(args: Namespace):
    with CalendarConnection(args.calendar) as conn:
        sync = Synchronizer(conn)
        concerts = TaborankaConcerts().get_concerts()
        sync.sync_concerts(concerts or [])


def create_arg_parser() -> ArgumentParser:
    parser = ArgumentParser()
    
    parser.add_argument('--group', choices=['taboranka'], default=['taboranka'], type=list)

    subparsers = parser.add_subparsers(title='action', dest='action')

    print_parser = subparsers.add_parser('print', help='Prints fetched data into gcal (default)')
    print_parser.add_argument('-e', '--as-events', help='Print fetched concerts as gcal events', action=BooleanOptionalAction)

    sync_parser = subparsers.add_parser('sync', help='Syncs fetched data into gcal')
    sync_parser.add_argument('-c', '--calendar', help='Google Calendar ID', required=True, type=str)
    sync_parser.add_argument('-l', '--list', help='List all events in calendar created by this app', metavar='list', action=BooleanOptionalAction)

    parser.set_defaults(action='print')
    return parser


def run(args):
    if args.action == 'print':
        handle_print(args)

    if args.action == 'sync':
        print(args)
        handle_sync(args)

if __name__ == '__main__':
    args = create_arg_parser().parse_args()
    run(args)

