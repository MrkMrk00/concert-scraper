from scraper.taboranka import TaborankaConcerts 

def run():
    concerts = TaborankaConcerts().get_concerts()

    for c in concerts or []:
        print(str(c))

if __name__ == '__main__':
    run()
