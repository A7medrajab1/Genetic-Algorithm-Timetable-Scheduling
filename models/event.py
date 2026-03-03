class Event:
    """
    Represents a single teaching event (one lecture, one session).
    
    This is the atomic unit that the GA must place into a (timeslot, room) pair.
    
    Attributes:
        id (int): Unique identifier.
        name (str): Human-readable name (e.g., "CS101 Lecture").
        lecturer_id (int): ID of the assigned lecturer.
        student_group_ids (list[int]): IDs of all student groups attending.
        size (int): Total number of students expected.
        duration (int): Number of consecutive timeslots required (1 for now).
    """
    
    def __init__(self, id: int, lecturer_id: int,
                 student_group_ids: list, size: int,
                 name: str = None, duration: int = 1):
        self.id = id
        self.name = name or f"Event_{id}"
        self.lecturer_id = lecturer_id
        self.student_group_ids = student_group_ids  # list of group IDs
        self.size = size
        self.duration = duration  # always 1 for now
    
    def __repr__(self):
        return (f"Event(id={self.id}, name='{self.name}', "
                f"lecturer={self.lecturer_id}, "
                f"groups={self.student_group_ids}, size={self.size})")
    
    def __eq__(self, other):
        return isinstance(other, Event) and self.id == other.id
    
    def __hash__(self):
        return hash(self.id)