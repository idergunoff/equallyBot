from sqlalchemy import create_engine, Column, Integer, BigInteger, String, Date, DateTime, Time, Text, Boolean, ForeignKey, Float, func
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship


# DATABASE_NAME = 'idergunoff:slon9124@localhost:5432/equally_db'
DATABASE_NAME = 'idergunoff:slon9124@ovz1.j56960636.m29on.vps.myjino.ru:49359/equally_db'

engine = create_engine(f'postgresql+psycopg2://{DATABASE_NAME}', echo=False)
Session = sessionmaker(bind=engine)

Base = declarative_base()


class User(Base):
    __tablename__ = 'user'

    telegram_id = Column(BigInteger, primary_key=True)
    name = Column(String)

    events = relationship('Event', back_populates='user')


class Event(Base):
    __tablename__ = 'event'

    id = Column(Integer, primary_key=True)
    user_id = Column(BigInteger, ForeignKey('user.telegram_id'))
    title = Column(String)
    current_event = Column(Boolean, default=True)

    user = relationship('User', back_populates='events')
    participants = relationship('Participant', back_populates='event')


class Participant(Base):
    __tablename__ = 'participant'

    id = Column(Integer, primary_key=True)
    event_id = Column(Integer, ForeignKey('event.id'))
    name = Column(String)
    spent = Column(Float, default=0)
    debt = Column(Float, default=0)

    event = relationship('Event', back_populates='participants')
    expenses = relationship('Expense', back_populates='participant')
    exclusions = relationship('Exclusion', back_populates='participant')


class Expense(Base):
    __tablename__ = 'expense'

    id = Column(Integer, primary_key=True)
    title = Column(String)
    price = Column(Float)
    participant_id = Column(Integer, ForeignKey('participant.id'))

    participant = relationship('Participant', back_populates='expenses')
    exclusions = relationship('Exclusion', back_populates='expense')


class Exclusion(Base):
    __tablename__ = 'exclusion'

    id = Column(Integer, primary_key=True)
    participant_id = Column(Integer, ForeignKey('participant.id'))
    expense_id = Column(Integer, ForeignKey('expense.id'))

    participant = relationship('Participant', back_populates='exclusions')
    expense = relationship('Expense', back_populates='exclusions')


Base.metadata.create_all(engine)