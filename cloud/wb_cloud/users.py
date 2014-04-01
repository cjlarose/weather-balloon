from datetime import datetime

from sqlalchemy.sql.functions import now, sum
from sqlalchemy.sql.expression import case, extract, cast, desc
from sqlalchemy.sql import func
from sqlalchemy.types import DateTime

from wb_cloud.models import (
    Instance,
    InstanceType,
    User,
)

def leaderboard_query(session, start_date, until_date):
    """
    This is, admittedly, a really ugly sql query. Query optimization has not
    been performed, but it shouldn't be anything more complicated than a few
    indices. Good luck.
    """
    #start_date = datetime.strptime(start_date, '%Y-%m-%d')
    #until_date = datetime.strptime(until_date_str, '%Y-%m-%d')
    subq = session\
        .query(
            Instance,
            InstanceType,
            User,
            case([(Instance.end_date != None, Instance.end_date)], else_=now()).label('stop_date'))\
        .join(Instance.user)\
        .join(Instance.type)\
        .subquery()

    uptime_column = case(
        [
            (subq.c.created_date > until_date, 0),
            (subq.c.stop_date < start_date, 0)
        ],
        else_=extract('epoch',
            func.LEAST(subq.c.stop_date, cast(until_date, DateTime)) -
            func.GREATEST(subq.c.created_date, cast(start_date, DateTime))
        )
    )

    print subq.c
    subq2 = session.query(
        subq.c.user_id,
        sum(case([(uptime_column == 0, 0)], else_=1)).label('instance_count'),
        #func.count(subq.c.instance_id).label('instance_count'),
        sum(uptime_column).label('uptime'),
        sum(uptime_column * subq.c.cpu).label('cpu_seconds')
    ).group_by(subq.c.user_id).order_by(desc('cpu_seconds')).subquery()

    q = session.query(
        subq2.c.user_id,
        subq2.c.uptime,
        subq2.c.cpu_seconds,
        subq2.c.instance_count,
        User.username,
        User.is_staff,
        User.name
    ).join(User)

    return q
