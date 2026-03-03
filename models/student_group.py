class StudentGroup:
    """
    Represents a cohort of students who share the same set of courses.
    
    Attributes:
        id (int): Unique identifier.
        name (str): Human-readable name (e.g., "CS Year 2 Group A").
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