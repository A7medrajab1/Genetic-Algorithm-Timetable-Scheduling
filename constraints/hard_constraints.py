"""
Hard Constraint Checking Module

Implements the five hard constraints from the scoped problem:
    H1 — Lecturer Uniqueness
    H2 — Student Group Uniqueness
    H3 — Room Uniqueness
    H4 — Room Capacity
    H6 — Lecturer Availability

These are used by the Schedule Builder to determine if an event
can be legally placed in a (timeslot, room) pair given the
current partial timetable.
"""


def check_lecturer_uniqueness(event, timeslot_id, current_assignments):
    """
    H1: A lecturer cannot teach two events at the same timeslot.
    
    Args:
        event: The Event object to be placed.
        timeslot_id: The candidate timeslot ID.
        current_assignments: dict mapping timeslot_id -> list of
                             (event, room) tuples already placed.
    
    Returns:
        bool: True if no conflict, False if violation.
    """
    if timeslot_id not in current_assignments:
        return True
    
    for assigned_event, _ in current_assignments[timeslot_id]:
        if assigned_event.lecturer_id == event.lecturer_id:
            return False
    return True


def check_student_group_uniqueness(event, timeslot_id, current_assignments):
    """
    H2: A student group cannot attend two events at the same timeslot.
    
    Args:
        event: The Event object to be placed.
        timeslot_id: The candidate timeslot ID.
        current_assignments: dict mapping timeslot_id -> list of
                             (event, room) tuples already placed.
    
    Returns:
        bool: True if no conflict, False if violation.
    """
    if timeslot_id not in current_assignments:
        return True
    
    event_groups = set(event.student_group_ids)
    
    for assigned_event, _ in current_assignments[timeslot_id]:
        assigned_groups = set(assigned_event.student_group_ids)
        # If any student group overlaps, it's a clash
        if event_groups & assigned_groups:  # set intersection
            return False
    return True


def check_room_uniqueness(timeslot_id, room_id, current_assignments):
    """
    H3: A room cannot host more than one event per timeslot.
    
    Args:
        timeslot_id: The candidate timeslot ID.
        room_id: The candidate room ID.
        current_assignments: dict mapping timeslot_id -> list of
                             (event, room) tuples already placed.
    
    Returns:
        bool: True if no conflict, False if violation.
    """
    if timeslot_id not in current_assignments:
        return True
    
    for _, assigned_room in current_assignments[timeslot_id]:
        if assigned_room.id == room_id:
            return False
    return True


def check_room_capacity(event, room):
    """
    H4: Event size must be <= room capacity.
    
    Args:
        event: The Event object.
        room: The Room object.
    
    Returns:
        bool: True if room is large enough, False otherwise.
    """
    return event.size <= room.capacity


def check_lecturer_availability(event, timeslot_id, lecturers_dict):
    """
    H6: Event cannot be scheduled when the lecturer is unavailable.
    
    Args:
        event: The Event object.
        timeslot_id: The candidate timeslot ID.
        lecturers_dict: dict mapping lecturer_id -> Lecturer object.
    
    Returns:
        bool: True if lecturer is available, False otherwise.
    """
    lecturer = lecturers_dict.get(event.lecturer_id)
    if lecturer is None:
        return True  # If lecturer not found, assume available
    return lecturer.is_available(timeslot_id)


def check_all_hard_constraints(event, timeslot_id, room, 
                                current_assignments, lecturers_dict):
    """
    Master function: checks ALL hard constraints for placing an event
    in a (timeslot, room) pair.
    
    Returns:
        bool: True if ALL hard constraints are satisfied.
    """
    # H1: Lecturer uniqueness
    if not check_lecturer_uniqueness(event, timeslot_id, current_assignments):
        return False
    
    # H2: Student group uniqueness
    if not check_student_group_uniqueness(event, timeslot_id, current_assignments):
        return False
    
    # H3: Room uniqueness
    if not check_room_uniqueness(timeslot_id, room.id, current_assignments):
        return False
    
    # H4: Room capacity
    if not check_room_capacity(event, room):
        return False
    
    # H6: Lecturer availability
    if not check_lecturer_availability(event, timeslot_id, lecturers_dict):
        return False
    
    return True