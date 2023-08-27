from scraper.models import Concert, ConcertCollection
from scraper.taboranka import TaborankaConcerts 
from argparse import ArgumentParser, Namespace


GROUPS: dict[str, type[ConcertCollection]] = {
    'taboranka': TaborankaConcerts,
}

def handle_print(args: Namespace):
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

