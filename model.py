from sqlalchemy import create_engine, Column, Integer, BigInteger, String, Date, DateTime, Time, Text, Boolean, ForeignKey, Float, func
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship


# DATABASE_NAME = 'idergunoff:slon9124@localhost:5432/equally_db'
DATABASE_NAME = 'idergunoff:slon9124@ovz1.j56960636.m29on.vps.myjino.ru:49359/equally_db'

engine = create_engine(f'postgresql+psycopg2://{DATABASE_NAME}', echo=False)
Session = sessionmaker(bind=engine)

Base = declarative_base()





Base.metadata.create_all(engine)