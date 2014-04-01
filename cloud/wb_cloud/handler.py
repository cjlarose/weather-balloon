from datetime import datetime

from wb_services.cloud import Cloud
from wb_cloud.users import leaderboard_query

class Handler(Cloud.Iface):

    def __init__(self, session):
        self.session = session

    def get_leaderboard(self, start_date, until_date):
        start_date = datetime.utcfromtimestamp(start_date)
        until_date = datetime.utcfromtimestamp(until_date)
        results = leaderboard_query(self.session, start_date, until_date).all()
        return Handler.format_results(results)

    def get_user_stats(self, start_date, until_date, username):
        start_date = datetime.utcfromtimestamp(start_date)
        until_date = datetime.utcfromtimestamp(until_date)
        results = leaderboard_query(self.session, start_date, until_date).all()
        # TODO perform the filter in SQL
        results = filter(lambda u: u.username == username, results)
        return Handler.format_results(results)

    @staticmethod
    def format_results(results):
        out = [{
            "username" : username,
            "is_staff": is_staff,
            "total_uptime": int(uptime) if uptime else None,
            "total_cpu_time": int(cpu_seconds) if cpu_seconds else None,
            "instance_count": instance_count
        } for uid, uptime, cpu_seconds, instance_count, username, is_staff, name in results
        if cpu_seconds and uptime]

        return out
