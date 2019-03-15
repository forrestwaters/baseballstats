import requests
from bs4 import BeautifulSoup


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
            print(url)
            return None


players = {}
for link in fetch_html('https://www.fangraphs.com/players.aspx').select('.s_name a'):
    print('https://www.fangraphs.com/' + link['href'])
    print(fetch_html('https://www.fangraphs.com/' + link['href']).select('.search table')[1])
    #for entry in fetch_html('https://www.fangraphs.com/' + link['href']).select('.search table').find_all('td'):
        #players[entry.text] = entry.next['href']

print(players)

