from baseball.baseball_players import setup_sql_session, Player

DB_NAME = 'baseball_stats.db'

session = setup_sql_session(DB_NAME)
for player in session.query(Player).all():
    print(player.fg_id)
    print(player.name)
