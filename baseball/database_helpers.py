from sqlalchemy import create_engine, Column, Integer, Float, String
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class Team(Base):
    """
    :param Base: sqlalchemy declarative_base https://docs.sqlalchemy.org/en/latest/orm/extensions/declarative/basic_use.html
    """
    __tablename__ = 'teams'
    id = Column(Integer, primary_key=True)
    team_name = Column(String)
    abbr = Column(String)


class Player(Base):
    __tablename__ = 'players'
    br_name = Column('br_name', String, primary_key=True)
    fg_id = Column('fg_id', String)
    name = Column('name', String)
    href = Column('href', String)
    position = Column('position', String)
    age = Column('age', Integer)
    team = Column('team', String)

    def __init__(self, br_name, fg_id, href, name, position, team):
        """
        :param br_name: baseball reference unique identifier that can be used for pulling
                        more stats for this specific player
        :param href: url for the specific players page
        :param name: Name of player
        :param position: Players position
        :param age: Players age
        :param team: Players current team
        """
        self.br_name = br_name
        self.fg_id = fg_id
        self.href = href
        self.name = name
        self.position = position
        self.team = team
        self.stats = None


class CareerStats(Base):
    __tablename__ = 'battercareerstats'
    br_name = Column('br_name', String, primary_key=True)
    name = Column('name', String)
    position = Column('position', String)
    G = Column(Integer)
    PA = Column(Integer)
    AB = Column(Integer)
    R = Column(Integer)
    H = Column(Integer)
    doubles = Column(Integer)
    triples = Column(Integer)
    HR = Column(Integer)
    RBI = Column(Integer)
    SB = Column(Integer)
    CS = Column(Integer)
    BB = Column(Integer)
    SO = Column(Integer)
    TB = Column(Integer)
    GIDP = Column(Integer)
    HBP = Column(Integer)
    SH = Column(Integer)
    SF = Column(Integer)
    IBB = Column(Integer)
    batting_avg = Column(Float)
    onbase_perc = Column(Float)
    slugging_perc = Column(Float)
    onbase_plus_slugging = Column(Float)
    onbase_plus_slugging_plus = Column(Float)
