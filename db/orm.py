import datetime
import logging
import os

import sqlalchemy
from sqlalchemy.future import select

from db.database import async_session_factory
from db.models import UserSubscriptions


class BaseAsyncORM:

    async def __aenter__(self):
        self._session = async_session_factory()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if exc_type is not None:
            logging.error(exc_type)
            logging.error(exc_val)
            logging.error(exc_tb)
            await self._session.rollback()
            raise exc_type(exc_val)
        else:
            await self._session.flush()
            await self._session.commit()

    async def add_subscription(self, telegram_id, article):
        user_subscription = UserSubscriptions(telegram_id=telegram_id, article=article,
                                              last_request_time=datetime.datetime.now(), request_time=datetime.datetime.now())
        self._session.add(user_subscription)

    async def delete_subscriptions(self, telegram_id):
        query = sqlalchemy.delete(UserSubscriptions).where(UserSubscriptions.telegram_id == telegram_id)
        await self._session.execute(query)

    async def get_subscription(self, ):
        query = select(UserSubscriptions).filter(
            UserSubscriptions.last_request_time <= datetime.datetime.now() - datetime.timedelta(
                seconds=int(os.getenv('TIME_PERIOD'))))
        sub_list = (await self._session.execute(query)).scalars().all()
        return sub_list

    async def set_last_request_time(self, subscription):
        subscription.last_request_time = datetime.datetime.now()

    async def get_last_five_subs(self, telegram_id):
        print(telegram_id)
        query = select(UserSubscriptions).filter(UserSubscriptions.telegram_id == telegram_id).order_by(
            UserSubscriptions.request_time.desc()).limit(5)
        sub_list = (await self._session.execute(query)).scalars()
        return sub_list