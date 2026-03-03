"""
Schedule Builder — The Genotype-to-Phenotype Decoder

This is the most critical component of the indirect-representation GA.

Given a chromosome (a permutation/priority list of event IDs), this module
constructs a feasible timetable by placing events one by one into the
first (timeslot, room) pair that satisfies ALL hard constraints.

If an event cannot be placed in ANY slot, it is recorded as "unplaced"
and a catastrophic penalty is applied during fitness evaluation.
"""

from constraints.hard_constraints import check_all_hard_constraints
from collections import defaultdict


class ScheduleBuilder:
    """
    Deterministic schedule builder that decodes a chromosome into a timetable.
    
    Attributes:
        timeslots (list): All available Timeslot objects, ordered by ID.
        rooms (list): All available Room objects, sorted by capacity ascending
                      (prefer smallest feasible room — helps room utilization).
        lecturers_dict (dict): Mapping of lecturer_id -> Lecturer object.
        events_dict (dict): Mapping of event_id -> Event object.
    """
    
    def __init__(self, timeslots, rooms, lecturers_dict, events_dict):
        self.timeslots = sorted(timeslots, key=lambda t: t.id)
        # Sort rooms by capacity ascending: the builder will try smaller
        # rooms first, which naturally helps room utilization even though
        # S10 is not in our scope. This is a "free" heuristic improvement.
        self.rooms = sorted(rooms, key=lambda r: r.capacity)
        self.lecturers_dict = lecturers_dict
        self.events_dict = events_dict
    
    def build(self, chromosome):
        """
        Decode a chromosome (permutation of event IDs) into a timetable.
        
        Algorithm:
            For each event_id in the chromosome order:
                For each timeslot (ordered):
                    For each room (ordered by capacity ascending):
                        If all hard constraints (H1, H2, H3, H4, H6) pass:
                            Assign event to (timeslot, room)
                            Break to next event
                If no valid (timeslot, room) found:
                    Record event as unplaced
        
        Args:
            chromosome (list[int]): Ordered list of event IDs (the permutation).
        
        Returns:
            tuple: (timetable, unplaced_events)
                - timetable: dict mapping event_id -> (timeslot_id, room_id)
                - unplaced_events: list of event_ids that could not be placed
        """
        # current_assignments: timeslot_id -> list of (Event, Room) tuples
        # This is the "partial timetable" used for constraint checking
        current_assignments = defaultdict(list)
        
        # Final timetable: event_id -> (timeslot_id, room_id)
        timetable = {}
        
        # Events that could not be placed feasibly
        unplaced_events = []
        
        for event_id in chromosome:
            event = self.events_dict[event_id]
            placed = False
            
            for timeslot in self.timeslots:
                if placed:
                    break
                for room in self.rooms:
                    if check_all_hard_constraints(
                        event=event,
                        timeslot_id=timeslot.id,
                        room=room,
                        current_assignments=current_assignments,
                        lecturers_dict=self.lecturers_dict
                    ):
                        # Place the event
                        timetable[event_id] = (timeslot.id, room.id)
                        current_assignments[timeslot.id].append((event, room))
                        placed = True
                        break
            
            if not placed:
                unplaced_events.append(event_id)
        
        return timetable, unplaced_events