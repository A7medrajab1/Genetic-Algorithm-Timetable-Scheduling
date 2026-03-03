class Lecturer:
    """
    Represents a faculty member / instructor.
    
    Attributes:
        id (int): Unique identifier.
        name (str): Human-readable name.
        unavailable_timeslots (set[int]): Set of timeslot IDs where the lecturer
                                          CANNOT be scheduled (hard constraint H6).
        preferred_timeslots (set[int]): Set of timeslot IDs the lecturer PREFERS
                                        (soft constraint S5). Scheduling outside
                                        these incurs a penalty.
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
        # If no preferences specified, every slot is acceptable
        if not self.preferred_timeslots:
            return True
        return timeslot_id in self.preferred_timeslots
    
    def __repr__(self):
        return f"Lecturer(id={self.id}, name='{self.name}')"
    
    def __eq__(self, other):
        return isinstance(other, Lecturer) and self.id == other.id
    
    def __hash__(self):
        return hash(self.id)