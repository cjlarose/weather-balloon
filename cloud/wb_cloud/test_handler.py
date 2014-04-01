from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from wb_cloud.settings import config
from wb_cloud.handler import Handler

engine = create_engine(config['db_url'])
Session = sessionmaker(bind=engine)
handler = Handler(Session())
