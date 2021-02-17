from sqlalchemy import Column, String, Integer, create_engine
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class GatekeeperBans(Base):
    __tablename__ = "gk_bans"
    id = Column(Integer, primary_key=True)
    user_id = Column(String)
    reason = Column(String, default="No reason provided")
    moderator = Column(String)

class GatekeeperMods(Base):
    __tablename__ = "gk_mods"
    id = Column(Integer, primary_key=True)
    user_id = Column(String)

def get_session(pg_url: str):
    engine = create_engine(pg_url, pool_size=0, pool_recycle=3600)
    from sqlalchemy.orm import sessionmaker
    session = sessionmaker()
    session.configure(bind=engine)
    return session

def setup(bot):
    print("Establishing DB connection")
    bot.Sql = get_session(bot.pg_url)
    print("Done")
