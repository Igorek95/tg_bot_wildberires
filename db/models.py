import sqlalchemy as sql

from db.database import Base, sync_engine


class UserSubscriptions(Base):
    __tablename__ = 'user_subscriptions'
    id = sql.Column(sql.Integer, primary_key=True)
    telegram_id = sql.Column(sql.BigInteger)
    article = sql.Column(sql.BigInteger)
    last_request_time = sql.Column(sql.DateTime)
    request_time = sql.Column(sql.DateTime)


Base.metadata.create_all(sync_engine)