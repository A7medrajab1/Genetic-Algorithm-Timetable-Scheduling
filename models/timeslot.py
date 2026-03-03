class Timeslot:
    """
    Represents a single discrete timeslot in the weekly schedule.
    
    Schedule Structure:
        Days: Saturday(0), Sunday(1), Monday(2), Tuesday(3), 
              Wednesday(4), Thursday(5)
        Periods: 3 per day, each 2 hours
            Period 0: 08:00 - 10:00
            Period 1: 10:00 - 12:00
            Period 2: 12:00 - 14:00
    
    Total: 6 days x 3 periods = 18 timeslots
    
    Attributes:
        id (int): Unique identifier for this timeslot.
        day (int): Day of the week (0=Saturday, ..., 5=Thursday).
        period (int): Period within the day (0, 1, or 2).
    """
    
    DAY_NAMES = ["Saturday", "Sunday", "Monday", 
                 "Tuesday", "Wednesday", "Thursday"]
    
    PERIOD_LABELS = {
        0: "08:00-10:00",
        1: "10:00-12:00",
        2: "12:00-14:00",
    }
    
    def __init__(self, id: int, day: int, period: int):
        self.id = id
        self.day = day
        self.period = period
    
    @property
    def day_name(self):
        """Return the human-readable day name."""
        if self.day < len(self.DAY_NAMES):
            return self.DAY_NAMES[self.day]
        return f"Day{self.day}"
    
    @property
    def period_label(self):
        """Return the human-readable time range."""
        return self.PERIOD_LABELS.get(self.period, f"Period{self.period}")
    
    def __repr__(self):
        return (f"Timeslot(id={self.id}, {self.day_name}, "
                f"{self.period_label})")
    
    def __eq__(self, other):
        return isinstance(other, Timeslot) and self.id == other.id
    
    def __hash__(self):
        return hash(self.id)