from datetime import datetime
from core.config import get_supabase

class Meeting:
    TABLE = 'meetings'
    
    def __init__(self, data):
        self.id = data.get('id')
        self.venue_code = data.get('venue_code')
        self.meeting_date = data.get('meeting_date')
        self.meeting_name = data.get('meeting_name')
        self.created_at = data.get('created_at')
    
    @classmethod
    def get_or_create(cls, venue_code, meeting_date):
        supabase = get_supabase()
        
        response = supabase.table(cls.TABLE)\
            .select('*')\
            .eq('venue_code', venue_code)\
            .eq('meeting_date', meeting_date)\
            .execute()
        
        if response.data:
            return cls(response.data[0])
        
        data = {
            'venue_code': venue_code,
            'meeting_date': meeting_date,
            'meeting_name': f"Réunion {venue_code} - {meeting_date}"
        }
        response = supabase.table(cls.TABLE).insert(data).execute()
        return cls(response.data[0])
    
    @classmethod
    def get_all(cls):
        supabase = get_supabase()
        response = supabase.table(cls.TABLE).select('*').execute()
        return [cls(item) for item in response.data]


class Race:
    TABLE = 'races'
    
    def __init__(self, data):
        self.id = data.get('id')
        self.meeting_id = data.get('meeting_id')
        self.race_no = data.get('race_no')
        self.race_name = data.get('race_name')
        self.total_runners = data.get('total_runners')
        self.created_at = data.get('created_at')


class Runner:
    TABLE = 'runners'
    
    def __init__(self, data):
        self.id = data.get('id')
        self.race_id = data.get('race_id')
        self.runner_no = data.get('runner_no')
        self.horse_name = data.get('horse_name')
        self.rating = data.get('rating')
        self.weight = data.get('weight')
        self.draw = data.get('draw')
        self.trainer = data.get('trainer')
        self.jockey = data.get('jockey')
        self.win_odds = data.get('win_odds')
        self.is_winner = data.get('is_winner', False)
        self.created_at = data.get('created_at')


class Bet:
    TABLE = 'bets'
    
    def __init__(self, data):
        self.id = data.get('id')
        self.runner_id = data.get('runner_id')
        self.race_id = data.get('race_id')
        self.horse_name = data.get('horse_name')
        self.stake = data.get('stake')
        self.odds = data.get('odds')
        self.probability = data.get('probability')
        self.result = data.get('result', 'PENDING')
        self.profit = data.get('profit', 0)
        self.created_at = data.get('created_at')
    
    def save(self):
        supabase = get_supabase()
        data = {
            'runner_id': self.runner_id,
            'race_id': self.race_id,
            'horse_name': self.horse_name,
            'stake': self.stake,
            'odds': self.odds,
            'probability': self.probability,
            'result': self.result,
            'profit': self.profit
        }
        if self.id:
            response = supabase.table(self.TABLE).update(data).eq('id', self.id).execute()
        else:
            response = supabase.table(self.TABLE).insert(data).execute()
            self.id = response.data[0]['id']
        return self
    
    @classmethod
    def get_all(cls):
        supabase = get_supabase()
        response = supabase.table(cls.TABLE).select('*').execute()
        return [cls(item) for item in response.data]
    
    @classmethod
    def get_stats(cls):
        bets = cls.get_all()
        total = len(bets)
        wins = sum(1 for b in bets if b.result == 'WIN')
        total_profit = sum(b.profit or 0 for b in bets)
        
        return {
            'total_bets': total,
            'wins': wins,
            'losses': total - wins,
            'win_rate': (wins / total * 100) if total > 0 else 0,
            'total_profit': total_profit,
            'avg_stake': sum(b.stake or 0 for b in bets) / total if total > 0 else 0
        }


class Result:
    TABLE = 'results'
    
    def __init__(self, data):
        self.id = data.get('id')
        self.race_id = data.get('race_id')
        self.winner_number = data.get('winner_number')
        self.winner_name = data.get('winner_name')
        self.created_at = data.get('created_at')
    
    @classmethod
    def save_result(cls, race_id, winner_number, winner_name):
        supabase = get_supabase()
        
        existing = supabase.table(cls.TABLE)\
            .select('*')\
            .eq('race_id', race_id)\
            .execute()
        
        if existing.data:
            response = supabase.table(cls.TABLE)\
                .update({
                    'winner_number': winner_number,
                    'winner_name': winner_name
                })\
                .eq('race_id', race_id)\
                .execute()
            return cls(response.data[0])
        
        data = {
            'race_id': race_id,
            'winner_number': winner_number,
            'winner_name': winner_name
        }
        response = supabase.table(cls.TABLE).insert(data).execute()
        return cls(response.data[0])