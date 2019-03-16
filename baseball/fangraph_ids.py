from baseball.baseball_players import fetch_html
from time import sleep


def get_fg_ids():
    fgp = dict()
    for link in fetch_html('https://www.fangraphs.com/players.aspx').select('.s_name a'):
        for entry in fetch_html('https://www.fangraphs.com/' + link['href']).select('.search table'):
            for player in entry.find_all('tr'):
                fgp[player.find('a').text] = player.find('a')['href'].split('=')[1].rstrip('&position')
            sleep(1)
            print(fgp)
