import sqlalchemy as sq
from sqlalchemy import MetaData, create_engine
from sqlalchemy.orm import Session, declarative_base

from config import db_vkinder_connect

MetaData = MetaData()
Base = declarative_base()
engine = create_engine(db_vkinder_connect)


class SeenUsers(Base):
    __tablename__ = 'users'
    user_id = sq.Column(sq.Integer, primary_key = True)
    found_users = sq.Column(sq.Integer, primary_key=True)


def add_user(engine, user_id, found_user):
    with Session(engine) as session:
        to_bd = SeenUsers(user_id = user_id, found_users = found_user)
        session.add(to_bd)
        session.commit()


def check_seen_users(engine, user_id, found_user):
    with Session(engine) as session:
        from_bd = session.query(SeenUsers).filter(
            SeenUsers.user_id == user_id,
            SeenUsers.found_users == found_user
        ).first()
        return True if from_bd else False
        

if __name__ == '__main__':
    engine = create_engine(db_vkinder_connect)
    Base.metadata.create_all(engine)