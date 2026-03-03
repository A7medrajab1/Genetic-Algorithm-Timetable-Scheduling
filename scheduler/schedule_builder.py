"""
Schedule Builder — The Genotype-to-Phenotype Decoder (v3)

SIMPLE GREEDY FIRST-FIT BUILDER:

    This builder ONLY enforces hard constraints.
    It does NOT consider soft constraints at all.

    Algorithm:
        For each event (in chromosome order):
            Try each timeslot in FIXED order (0, 1, 2, ... 17)
            Try each room in FIXED order (smallest capacity first)
            Place in the FIRST feasible slot found
            Move to next event

    WHY SIMPLE?
        The v2 smart builder scored all placements and picked the best.
        This meant every chromosome produced a perfect timetable.
        The GA had nothing to optimize.

        With this simple builder:
        - Events early in chromosome get early timeslots (Saturday 08:00)
        - Events late in chromosome get late timeslots (Thursday 12:00)
        - If two events from the SAME group are early in the chromosome,
          they both land on Saturday → creates GAPS and CLUSTERING
        - If the GA spreads them apart in the chromosome,
          they land on different days → FEWER gaps and better spreading

        RESULT: Different chromosome orders produce genuinely different
        timetable qualities. The GA can now optimize.

    RESPONSIBILITY SPLIT:
        Builder → guarantees hard constraints (H1, H2, H3, H4, H6)
        GA      → optimizes soft constraints (S1a, S4, S5) via evolution
"""

from constraints.hard_constraints import check_all_hard_constraints
from collections import defaultdict


class ScheduleBuilder:
    """
    Simple greedy first-fit schedule builder.

    Hard constraints: GUARANTEED (H1, H2, H3, H4, H6)
    Soft constraints: NOT considered (left to GA)

    Attributes:
        timeslots (list): All Timeslot objects, sorted by ID (0 to 17).
        rooms (list): All Room objects, sorted by capacity ascending.
        lecturers_dict (dict): lecturer_id -> Lecturer object.
        events_dict (dict): event_id -> Event object.
    """

    def __init__(self, timeslots, rooms, lecturers_dict, events_dict):
        # Fixed order: timeslot 0 (Sat 08:00) first, timeslot 17 (Thu 12:00) last
        self.timeslots = sorted(timeslots, key=lambda t: t.id)
        # Smallest room first: prefer tight fit for capacity constraint
        self.rooms = sorted(rooms, key=lambda r: r.capacity)
        self.lecturers_dict = lecturers_dict
        self.events_dict = events_dict

    def build(self, chromosome):
        """
        Decode a chromosome into a timetable using simple first-fit.

        The chromosome is a permutation of event IDs like:
            [E16, E24, E0, E12, E6, ...]

        The builder processes events in THIS order.
        Each event gets the FIRST available (timeslot, room) pair.

        Example of why order matters:
            Chromosome A: [E0, E1, E2, ...]  (Y1 events first)
                E0 (Intro Programming, Y1) → Sat 08:00
                E1 (Discrete Math, Y1)     → Sat 10:00
                E2 (Calculus I, Y1)        → Sat 12:00
                → Y1 has 3 events on Saturday → GAPS possible, BAD spreading

            Chromosome B: [E0, E6, E12, E1, E7, E13, ...]  (alternating years)
                E0  (Intro Programming, Y1) → Sat 08:00
                E6  (Data Structures, Y2)   → Sat 08:00 (different room)
                E12 (Operating Systems, Y3) → Sat 08:00 (different room)
                E1  (Discrete Math, Y1)     → Sat 10:00
                → Events spread across groups → FEWER gaps, BETTER spreading

        Args:
            chromosome (list[int]): Ordered list of event IDs.

        Returns:
            tuple: (timetable, unplaced_events)
                - timetable: dict {event_id: (timeslot_id, room_id)}
                - unplaced_events: list of event_ids that could not be placed
        """
        # Tracks what is placed where (for constraint checking)
        # timeslot_id -> list of (Event, Room) tuples
        current_assignments = defaultdict(list)

        # Final output
        timetable = {}
        unplaced_events = []

        for event_id in chromosome:
            event = self.events_dict[event_id]
            placed = False

            # Try every timeslot in FIXED order (0, 1, 2, ... 17)
            for timeslot in self.timeslots:
                if placed:
                    break

                # Try every room in FIXED order (smallest capacity first)
                for room in self.rooms:
                    # Check ALL hard constraints
                    if check_all_hard_constraints(
                        event=event,
                        timeslot_id=timeslot.id,
                        room=room,
                        current_assignments=current_assignments,
                        lecturers_dict=self.lecturers_dict
                    ):
                        # FIRST feasible slot found → place it here
                        timetable[event_id] = (timeslot.id, room.id)
                        current_assignments[timeslot.id].append(
                            (event, room)
                        )
                        placed = True
                        break  # Stop trying rooms, move to next event

            if not placed:
                unplaced_events.append(event_id)

        return timetable, unplaced_events