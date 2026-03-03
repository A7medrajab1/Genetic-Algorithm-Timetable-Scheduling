class Room:
    """
    Represents a physical classroom or lecture hall.
    
    Attributes:
        id (int): Unique identifier.
        capacity (int): Maximum number of students the room can hold.
        name (str): Human-readable name (e.g., "Room 101").
    """
    
    def __init__(self, id: int, capacity: int, name: str = None):
        self.id = id
        self.capacity = capacity
        self.name = name or f"Room_{id}"
    
    def __repr__(self):
        return f"Room(id={self.id}, name='{self.name}', capacity={self.capacity})"
    
    def __eq__(self, other):
        return isinstance(other, Room) and self.id == other.id
    
    def __hash__(self):
        return hash(self.id)