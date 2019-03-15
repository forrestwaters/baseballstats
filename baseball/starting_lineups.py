import requests
from bs4 import BeautifulSoup

LINEUPS = "https://www.mlb.com/starting-lineups"


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
            print('Status code: %'.format(r.status_code))
            return None


class Matchup:
    def __init__(self, soup):
        self.soup = soup
        self.home_team = ''
        self.away_team = ''
        self.home_pitcher = ''
        self.away_pitcher = ''
        self.home_lineup = list()
        self.away_lineup = list()

    def get_teams(self):
        self.away_team = self.soup.select('.starting-lineups__game .starting-lineups__team-name--link')[0][
            'data-tri-code']
        self.home_team = self.soup.select('.starting-lineups__game .starting-lineups__team-name--link')[1][
            'data-tri-code']

    def get_pitchers(self):
        p = self.soup.select('.starting-lineups__pitchers')[0].select('.starting-lineups__pitcher-name')
        self.away_pitcher = p[0].text.strip('\n')
        self.home_pitcher = p[1].text.strip('\n')

    def get_lineups(self):
        away_soup = self.soup.find(attrs={'class': 'starting-lineups__team starting-lineups__team--away'})
        home_soup = self.soup.find(attrs={'class': 'starting-lineups__team starting-lineups__team--home'})
        self.home_lineup = [player.text for player in home_soup.select('.starting-lineups__player')]
        self.away_lineup = [player.text for player in away_soup.select('.starting-lineups__player')]

    def return_matchup_info(self):
        self.get_teams()
        self.get_pitchers()
        self.get_lineups()
        return {self.home_team: {'SP': self.home_pitcher, 'lineup': self.home_lineup},
                self.away_team: {'SP': self.away_pitcher, 'lineup': self.away_lineup}}


for matchup_soup in fetch_html(LINEUPS).select('.starting-lineups__matchup'):
    print(Matchup(matchup_soup).return_matchup_info())
