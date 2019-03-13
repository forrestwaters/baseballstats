import requests
from bs4 import BeautifulSoup

LINEUPS = "https://www.mlb.com/starting-lineups"

with requests.get(LINEUPS) as r:
    soup = BeautifulSoup(r.text)

games = soup.find(attrs={'class': 'starting-lineups'}).find('starting-lineups__container-multi--current').find_all(
    attrs={'class': 'starting-lineups__matchup'})


