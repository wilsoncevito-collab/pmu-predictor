from sqlalchemy import Column, String, Integer, Float, Boolean, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from core.config import Base, SessionLocal, get_db

class Meeting(Base):
    __tablename__ = 'meetings'
    id = Column(Integer, primary_key=True, autoincrement=True)
    venue_code = Column(String)
    meeting_date = Column(String)
    meeting_name = Column(String)
    created_at = Column(DateTime, default=datetime.now)

class Race(Base):
    __tablename__ = 'races'
    id = Column(Integer, primary_key=True, autoincrement=True)
    meeting_id = Column(Integer, ForeignKey('meetings.id'))
    race_no = Column(Integer)
    race_name = Column(String)
    total_runners = Column(Integer)
    created_at = Column(DateTime, default=datetime.now)

class Runner(Base):
    __tablename__ = 'runners'
    id = Column(Integer, primary_key=True, autoincrement=True)
    race_id = Column(Integer, ForeignKey('races.id'))
    runner_no = Column(Integer)
    horse_name = Column(String)
    rating = Column(Float)
    weight = Column(Integer)
    draw = Column(Integer)
    trainer = Column(String)
    jockey = Column(String)
    win_odds = Column(Float)
    is_winner = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.now)

class Bet(Base):
    __tablename__ = 'bets'
    id = Column(Integer, primary_key=True, autoincrement=True)
    runner_id = Column(Integer)
    race_id = Column(Integer)
    horse_name = Column(String)
    stake = Column(Float)
    odds = Column(Float)
    probability = Column(Float)
    result = Column(String, default='PENDING')
    profit = Column(Float, default=0)
    created_at = Column(DateTime, default=datetime.now)

class Result(Base):
    __tablename__ = 'results'
    id = Column(Integer, primary_key=True, autoincrement=True)
    race_id = Column(Integer)
    winner_number = Column(Integer)
    winner_name = Column(String)
    created_at = Column(DateTime, default=datetime.now)
    
    @classmethod
    def save_result(cls, race_id, winner_number, winner_name):
        db = get_db()
        existing = db.query(cls).filter(cls.race_id == race_id).first()
        if existing:
            existing.winner_number = winner_number
            existing.winner_name = winner_name
            result = existing
        else:
            result = cls(race_id=race_id, winner_number=winner_number, winner_name=winner_name)
            db.add(result)
        db.commit()
        db.close()
        return result

def init_db():
    from core.config import engine
    Base.metadata.create_all(bind=engine)