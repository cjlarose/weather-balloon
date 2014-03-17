from sqlalchemy import (Column, Integer, Text, String, DateTime, Boolean, 
    Numeric, ForeignKey)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.dialects import postgresql

from sqlalchemy.orm import backref, relationship

Base = declarative_base()

class Cloud(Base):
    __tablename__ = 'weather_balloon_cloud'
    id = Column(Integer, primary_key=True)
    name = Column(String(45), nullable=False)
    hostgroup_name = Column(String(45), nullable=False)
    instances = relationship("Instance", backref="cloud")
    images = relationship("Image", backref="cloud")

    instance_types = relationship("InstanceType", backref="cloud")

class Image(Base):
    __tablename__ = 'weather_balloon_image'
    id = Column(Integer, primary_key=True)
    image_id = Column(String(36), nullable=False)
    type = Column(String(32), nullable=False)
    cloud_id = Column(Integer, ForeignKey('weather_balloon_cloud.id'), nullable=False)

class Instance(Base):
    __tablename__ = 'weather_balloon_instance'
    id = Column(Integer, primary_key=True)
    instance_id = Column(String(36), nullable=False)
    address = Column(postgresql.INET)
    created_date = Column(DateTime(timezone=True), nullable=False)
    start_date = Column(DateTime(timezone=True))
    end_date = Column(DateTime(timezone=True))
    cloud_id = Column(Integer, ForeignKey('weather_balloon_cloud.id'), nullable=False)
    user_id = Column(Integer, ForeignKey('weather_balloon_user.id'), nullable=False)
    type_id = Column(Integer, ForeignKey('weather_balloon_instancetype.id'), nullable=False)
    image_id = Column(Integer, ForeignKey('weather_balloon_image.id'), nullable=False)
    client_name = Column(Text)

    user = relationship("User", backref=backref('instances'))
    image = relationship("Image", backref=backref('instances'))
    type = relationship("InstanceType", backref=backref('instances'))

class InstanceType(Base):
    __tablename__ = 'weather_balloon_instancetype'
    id = Column(Integer, primary_key=True)
    name = Column(String(45), nullable=False)
    cpu = Column(Integer)
    memory = Column(Integer)
    disk = Column(Integer)
    price = Column(Numeric(6,3))
    cloud_id = Column(Integer, ForeignKey('weather_balloon_cloud.id'), nullable=False)

class User(Base):
    __tablename__ = 'weather_balloon_user'
    id = Column(Integer, primary_key=True)
    username = Column(String(45), nullable=False)
    name = Column(String(100))
    mail = Column(String(100))
    is_staff = Column(Boolean)
