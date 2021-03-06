import requests
from bs4 import BeautifulSoup
from sqlalchemy import create_engine, Column, Integer, Float, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from time import sleep
from baseball.database_helpers import Team, Player, CareerStats
from baseball.database_helpers import Base

''' things to look for
 * batter vs pitcher hand
 * iso fangraphs if it's not on baseball ref?
 * statcast
'''

BR = 'https://www.baseball-reference.com/'
DB_NAME = 'baseball_stats.db'


def fetch_html(url):
    """
    :param url: any url to parse
    :return: returns a BeautifulSoup object if a 200 response is seen
    """
    with requests.get(url) as r:
        if r.status_code == 200:
            return BeautifulSoup(r.text, 'lxml')
        else:
            print('Received a non-200 response.')
            print('Status code: {}'.format(r.status_code))
            return None


def get_fg_ids():
    fgp = dict()
    for link in fetch_html('https://www.fangraphs.com/players.aspx').select('.s_name a'):
        if link is not None:
            h = fetch_html('https://www.fangraphs.com/' + link['href'])
            print(link['href'])
            if h is not None:
                for entry in h.select('.search table'):
                    for player in entry.find_all('tr'):
                        fgp[player.find('a').text] = player.find('a')['href'].split('=')[1].rstrip('&position')
                    sleep(1)
    return fgp


def get_teams(html):
    """
    :param html: BeautifulSoup html object from BR teams url
    :return: returns a dict object including team abbreviations and names
    """
    if html is not None:
        teams = {}
        for entry in html.find(attrs={'id': 'all_teams_active'}).find('tbody').find_all('td'):
            if entry.find('a') is not None:
                if len(entry.text.split(',')) > 1:
                    teams[entry.find('a').get('href').split('/')[2]] = entry.text.split(',')[1].replace('see ',
                                                                                                        '').strip(
                        ' ').replace(' ', '-').lower()
                else:
                    teams[entry.find('a').get('href').split('/')[2]] = entry.text.replace(' ', '-').lower()
        return teams


def populate_players_table(s, html, team, fg_ids):
    """
    :param s: sqlalchemy session
    :param html: BeautifulSoup object from players page
    :param team: team name passed in constructor because it's not in player row
    :param fg_ids: fangraph player ids
    :return:

    p['data-append-csv']
    href = p.find('a')['href']
    players name = p.find('a').text
    """
    players = html.find('tbody').find_all('td', attrs={'class': 'left'})
    count = 0
    while count < len(players):
        # little song and dance since player and position are on different rows
        position = players[count].text
        count += 1
        if not s.query(s.query(Player).filter_by(br_name=players[count]['data-append-csv']).exists()).scalar():
            s.add(Player(players[count]['data-append-csv'], fg_ids.get(players[count].find('a').text),
                         players[count].find('a')['href'], players[count].find('a').text, position, team))
        count += 1


def get_batter_career_stats(player, s):
    """
    :param player: Player() class object fetched from database
    :param s: sqlalchemy session
    :return: static method that adds the players stats dict to the session
    """
    soup = fetch_html(BR + player.href)
    stats = dict()
    stats['name'] = player.name
    stats['br_name'] = player.br_name
    stats['position'] = player.position
    # find the first tr footer for cases where 162 game average is calculated
    for v in soup.find('tfoot').find('tr').find_all('td'):
        if v.text is not '':
            if v['data-stat'] == '2B':
                stats['doubles'] = float(v.text)
            elif v['data-stat'] == '3B':
                stats['triples'] = float(v.text)
            else:
                stats[v['data-stat']] = float(v.text)
    s.add(CareerStats(**stats))


def setup_sql_session(dbname, base):
    """
    :param dbname: sqlite database name to write to
    :param base: sqlalchemy declarative_base https://docs.sqlalchemy.org/en/latest/orm/extensions/declarative/basic_use.html
    :return: sqlalchemy session that can be used easily
    """
    db = create_engine('sqlite:///{}'.format(dbname))
    base.metadata.create_all(db)
    s = sessionmaker()
    s.configure(bind=db)
    return s()


def populate_teams_table(s):
    """
    :param s: sqlalchemy session object created from setup_sql_session() method
    :return: static method - no return
    """
    if s.query(Team).count() == 0:
        for k, v in get_teams(fetch_html(BR + 'teams/')).items():
            s.add(Team(team_name=v, abbr=k))


if __name__ == '__main__':
    session = setup_sql_session(DB_NAME, Base)
    populate_teams_table(session)
    for team in session.query(Team).all():
        if team.abbr == 'ANA':
            tabbr = 'LAA'
        elif team.abbr == 'FLA':
            tabbr = 'MIA'
        elif team.abbr == 'TBD':
            tabbr = 'TBR'
        else:
            # BR is dumb and has names intertwined
            # will have to figure out how to be smarter about this
            tabbr = team.abbr
        populate_players_table(session, fetch_html(BR + 'teams/{}/2018.shtml'.format(tabbr)), tabbr, get_fg_ids())
#    for p in session.query(Player).all():
#        if p.position == 'P':
#            # get_pitcher_career_stats()
#            continue
#        else:
#            get_batter_career_stats(p, session)
    session.commit()
    session.close()
