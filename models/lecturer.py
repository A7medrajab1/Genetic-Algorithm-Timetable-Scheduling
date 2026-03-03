class Lecturer:
    """
    Represents a faculty member / instructor.
    
    Timeslot Reference (6 days x 3 periods = 18 slots):
        Saturday:  0,  1,  2
        Sunday:    3,  4,  5
        Monday:    6,  7,  8
        Tuesday:   9, 10, 11
        Wednesday: 12, 13, 14
        Thursday:  15, 16, 17
    
    Attributes:
        id (int): Unique identifier.
        name (str): Human-readable name.
        unavailable_timeslots (set[int]): Timeslot IDs where lecturer
                                          CANNOT teach (hard constraint H6).
        preferred_timeslots (set[int]): Timeslot IDs the lecturer PREFERS.
                                        Scheduling outside these = penalty (S5).
    """
    
    def __init__(self, id: int, name: str = None,
                 unavailable_timeslots: set = None,
                 preferred_timeslots: set = None):
        self.id = id
        self.name = name or f"Lecturer_{id}"
        self.unavailable_timeslots = unavailable_timeslots or set()
        self.preferred_timeslots = preferred_timeslots or set()
    
    def is_available(self, timeslot_id: int) -> bool:
        """Check if lecturer is available at a given timeslot (H6)."""
        return timeslot_id not in self.unavailable_timeslots
    
    def prefers(self, timeslot_id: int) -> bool:
        """Check if timeslot is among lecturer's preferred times (S5)."""
        if not self.preferred_timeslots:
            return True
        return timeslot_id in self.preferred_timeslots
    
    def __repr__(self):
        return f"Lecturer(id={self.id}, name='{self.name}')"
    
    def __eq__(self, other):
        return isinstance(other, Lecturer) and self.id == other.id
    
    def __hash__(self):
        return hash(self.id)