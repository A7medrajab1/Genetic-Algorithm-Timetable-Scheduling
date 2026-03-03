class StudentGroup:
    """
    Represents a cohort of students who share the same curriculum.
    
    One group = One department + One academic year.
    All students in the group take the same set of courses.
    
    The CONFLICT arises when one Event serves multiple groups:
        e.g., "Calculus I" serves CS_Y1 and Math_Y1.
        Therefore CS_Y1 and Math_Y1 cannot have other events
        at the same timeslot as Calculus I.
    
    Attributes:
        id (int): Unique identifier.
        name (str): Human-readable name (e.g., "CS_Year1").
        size (int): Number of students in this group.
    """
    
    def __init__(self, id: int, name: str = None, size: int = 0):
        self.id = id
        self.name = name or f"Group_{id}"
        self.size = size
    
    def __repr__(self):
        return f"StudentGroup(id={self.id}, name='{self.name}', size={self.size})"
    
    def __eq__(self, other):
        return isinstance(other, StudentGroup) and self.id == other.id
    
    def __hash__(self):
        return hash(self.id)