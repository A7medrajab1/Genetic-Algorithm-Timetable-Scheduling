class Timeslot:
    """
    Represents a single discrete timeslot in the weekly schedule.
    
    Attributes:
        id (int): Unique identifier for this timeslot.
        day (int): Day of the week (0=Monday, 1=Tuesday, ..., 4=Friday).
        period (int): Period within the day (0=first slot, 1=second, ...).
    """
    
    DAY_NAMES = ["Sunday", "Monday", "Tuesday", "Wednesday", "Thursday"]
    
    def __init__(self, id: int, day: int, period: int):
        self.id = id
        self.day = day
        self.period = period
    
    def __repr__(self):
        day_name = self.DAY_NAMES[self.day] if self.day < len(self.DAY_NAMES) else f"Day{self.day}"
        return f"Timeslot(id={self.id}, {day_name}, Period {self.period})"
    
    def __eq__(self, other):
        return isinstance(other, Timeslot) and self.id == other.id
    
    def __hash__(self):
        return hash(self.id)