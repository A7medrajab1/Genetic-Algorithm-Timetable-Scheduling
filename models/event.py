class Event:
    """
    Represents a single teaching event (one lecture, one session).
    
    This is the atomic unit that the GA must place into a (timeslot, room) pair.
    
    Attributes:
        id (int): Unique identifier.
        name (str): Human-readable name (e.g., "CS101 Lecture").
        lecturer_id (int): ID of the assigned lecturer.
        student_group_ids (list[int]): IDs of all student groups attending.
        duration (int): Number of consecutive timeslots required (1 for now).
        _size (int or None): If None, size is calculated dynamically from groups.
    """
    
    def __init__(self, id: int, lecturer_id: int,
                 student_group_ids: list,
                 name: str = None, duration: int = 1):
        self.id = id
        self.name = name or f"Event_{id}"
        self.lecturer_id = lecturer_id
        self.student_group_ids = student_group_ids
        self.duration = duration
        self._size = None  # Will be calculated dynamically
    
    def calculate_size(self, groups_dict):
        """
        Calculate total size by summing all attending group sizes.
        
        Args:
            groups_dict (dict): Mapping of group_id -> StudentGroup object.
        
        Example:
            Event with groups [0, 1]
            Group 0 size = 70, Group 1 size = 60
            Event size = 70 + 60 = 130
        """
        self._size = sum(
            groups_dict[gid].size 
            for gid in self.student_group_ids
        )
        return self._size
    
    @property
    def size(self):
        """Return the calculated size."""
        if self._size is None:
            raise ValueError(
                f"Event '{self.name}' (id={self.id}): "
                f"size not calculated yet. "
                f"Call calculate_size(groups_dict) first."
            )
        return self._size
    
    def __repr__(self):
        size_str = self._size if self._size is not None else "?"
        return (f"Event(id={self.id}, name='{self.name}', "
                f"lecturer={self.lecturer_id}, "
                f"groups={self.student_group_ids}, size={size_str})")
    
    def __eq__(self, other):
        return isinstance(other, Event) and self.id == other.id
    
    def __hash__(self):
        return hash(self.id)