from bs4 import BeautifulSoup
from sqlalchemy import create_engine, Column, Integer, String, Float, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from sqlalchemy_utils import UUIDType
import uuid
import requests
from fake_useragent import UserAgent
from queue import Queue
from threading import Thread


DB_NAME = 'baseball_stats.db'
TEAMS_URL = 'https://www.baseball-reference.com/teams/'
PLAYERS_URL = 'https://www.basketball-reference.com/leagues/NBA_2019_totals.html'
Base = declarative_base()


class Team(Base):
    __tablename__ = 'teams'
    id = Column(Integer, primary_key=True)
    team_name = Column(String)
    abbr = Column(String)


class Player(Base):
    __tablename__ = 'players'
    br_name = Column('br_name', String, primary_key=True)
    name = Column('name', String)
    href = Column('href', String)
    position = Column('position', String)
    age = Column('age', Integer)
    team = Column('team', String)
    playerstats = relationship("PlayerStats", back_populates="br_name")

    def __init__(self, br_name, href, name, position, age, team):
        self.br_name = br_name
        self.href = href
        self.name = name
        self.position = position
        self.age = age
        self.team = team
        self.stats = None

    def get_player_stats(self):
        self.stats = {}
        ua = UserAgent()
        with requests.get('https://www.basketball-reference.com' + self.href.rstrip('.html') + '/gamelog/2019',
                          headers={'User-Agent': ua.random}) as pstats:
            bsoup = BeautifulSoup(pstats.text, 'lxml')
        # Found that some players have no stats
        body = bsoup.find('tbody').find_all('tr')
        for game in body:
            cg = game.find_all(attrs={'class': 'right'})
            try:
                current_game = int(cg[0].text)
                # This assumes the first attribute pulled out is the 'ranker' attribute (which is the game number'
                # This has been true for all players I've looked at, but should probably do more validation
            except ValueError:
                continue
            if isinstance(current_game, int):
                self.stats[current_game] = {}
            for entry in game.find_all(attrs={'class': 'right'}):
                if entry['data-stat'] in STATS:
                    if entry.text == '':
                        self.stats[current_game][entry['data-stat']] = 0.0
                    if ':' in entry.text:
                        joined = entry.text.split(':')
                        self.stats[current_game][entry['data-stat']] = float(joined[0] + '.' + joined[1])

                    else:
                        try:
                            self.stats[current_game][entry['data-stat']] = float(entry.text)
                        except ValueError:
                            print(entry.text)
                else:
                    continue


def generate_uuid():
    return str(uuid.uuid4())


class PlayerStats(Base):
    __tablename__ = 'stats'
    id = Column(UUIDType(binary=False), primary_key=True, default=generate_uuid)
    name = Column(String, ForeignKey('players.br_name'))
    br_name = relationship("Player", back_populates="playerstats")
    game = Column(Integer)
    mp = Column(Float)
    fg = Column(Float)
    fga = Column(Float)
    fg_pct = Column(Float)
    fg3 = Column(Float)
    fg3_pct = Column(Float)
    ft = Column(Float)
    fta = Column(Float)
    ft_pct = Column(Float)
    orb = Column(Float)
    drb = Column(Float)
    trb = Column(Float)
    ast = Column(Float)
    stl = Column(Float)
    blk = Column(Float)
    tov = Column(Float)
    pts = Column(Float)


class PlayerStatsWorker(Thread):

    def __init__(self, queue):
        Thread.__init__(self)
        self.queue = queue

    def run(self):
        while True:
            player, s = self.queue.get()
            # Get the work from the queue and expand the tuple
            try:
                get_player_stats(player, s)
            finally:
                self.queue.task_done()


def setup_sql_session(dbname):
    db = create_engine('sqlite:///{}'.format(dbname))
    Base.metadata.create_all(db)
    s = sessionmaker()
    s.configure(bind=db)
    return s()


def populate_teams_table(s):
    # The teams in the nba shouldn't change - if anything exists in this table, leave it alone
    if s.query(Team).count() == 0:
        for k, v in TEAMS.items():
            s.add(Team(team_name=k, abbr=v))


def populate_players_table(s):
    with requests.get(PLAYERS_URL) as r:
        soup = BeautifulSoup(r.text, 'lxml')

    players = soup.find_all(attrs={'class': 'full_table'})
    for x in players:
        br_name = x.find_all('td')[0]['data-append-csv']
        if not s.query(s.query(Player).filter_by(br_name=br_name).exists()).scalar():
            s.add(Player(br_name, x.find_all('td')[0].find('a')['href'],
                         x.find_all('td')[0]['csk'], x.find_all('td')[1].text, x.find_all('td')[2].text,
                         x.find_all('td')[3].text, ))


def get_player_stats(player, s):
    game_stats = {}
    ua = UserAgent()
    with requests.get('https://www.basketball-reference.com' + player.href.rstrip('.html') + '/gamelog/2019',
                      headers={'User-Agent': ua.random}) as pstats:
        bsoup = BeautifulSoup(pstats.text, 'lxml')
    body = bsoup.find('tbody').find_all('tr')
    for game in body:
        cg = game.find_all(attrs={'class': 'right'})
        try:
            current_game = int(cg[0].text)
            # This assumes the first attribute pulled out is the 'ranker' attribute (which is the game number'
            # This has been true for all players I've looked at, but should probably do more validation
        except ValueError:
            continue
        if isinstance(current_game, int):
            game_stats['game'] = current_game
            game_stats['br_name'] = player
        for entry in game.find_all(attrs={'class': 'right'}):
            if entry['data-stat'] in STATS:
                if entry.text == '':
                    game_stats[entry['data-stat']] = 0.0
                if ':' in entry.text:
                    joined = entry.text.split(':')
                    game_stats[entry['data-stat']] = float(joined[0] + '.' + joined[1])

                else:
                    try:
                        game_stats[entry['data-stat']] = float(entry.text)
                    except ValueError:
                        print(entry.text)
            else:
                continue
        s.add(PlayerStats(**game_stats))


if __name__ == '__main__':
    session = setup_sql_session(DB_NAME)
    populate_teams_table(session)
    populate_players_table(session)
    session.commit()
    q = Queue()
    for x in range(8):
        worker = PlayerStatsWorker(q)
        worker.daemon = True
        worker.start()
    for p in session.query(Player):
        q.put((p, session))
    q.join()
    session.commit()
    session.close()
