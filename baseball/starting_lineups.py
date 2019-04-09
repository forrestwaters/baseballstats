from baseball.baseball_players import fetch_html


class Matchup:
    def __init__(self, soup):
        self.soup = soup

    def get_teams(self):
        """
        :return:  tuple of team abbr's (away, home)
        """
        return (self.soup.select('.starting-lineups__game .starting-lineups__team-name--link')[0]['data-tri-code'],
                self.soup.select('.starting-lineups__game .starting-lineups__team-name--link')[1]['data-tri-code'])

    def get_pitchers(self):
        p = self.soup.select('.starting-lineups__pitchers')[0].select('.starting-lineups__pitcher-name')
        return p[0].text.strip('\n'), p[1].text.strip('\n')

    def get_lineups(self):
        """

        :return: tuple - first object is away lineup, second is home lineup
        """
        home_soup = self.soup.find(attrs={'class': 'starting-lineups__team starting-lineups__team--home'})
        away_soup = self.soup.find(attrs={'class': 'starting-lineups__team starting-lineups__team--away'})
        return ([player.text for player in away_soup.select('.starting-lineups__player')],
                [player.text for player in home_soup.select('.starting-lineups__player')])

    def return_matchup_info(self):
        """
        Runs all important class methods
        :return: returns dictionary containing game info
        """
        teams = self.get_teams()
        pitchers = self.get_pitchers()
        lineups = self.get_lineups()
        return {teams[0]: {'SP': pitchers[0], 'lineup': lineups[0]},
                teams[1]: {'SP': pitchers[1], 'lineup': lineups[1]}}


def get_todays_matchups():
    daily_matchups = set()
    for matchup_soup in fetch_html("https://www.mlb.com/starting-lineups").select('.starting-lineups__matchup'):
        m = Matchup(matchup_soup)
        daily_matchups.add(m.return_matchup_info())
    return daily_matchups


print(get_todays_matchups())
