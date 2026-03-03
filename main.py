"""
Main Entry Point — UCTP Genetic Algorithm Solver

Creates a test dataset and runs the GA.

Test Dataset:
    - 5 days × 6 periods = 30 timeslots
    - 5 rooms (capacities 30 - 120)
    - 6 lecturers (with availability & preference constraints)
    - 8 student groups
    - 25 events
"""

import random
from models.timeslot import Timeslot
from models.room import Room
from models.lecturer import Lecturer
from models.student_group import StudentGroup
from models.event import Event
from scheduler.schedule_builder import ScheduleBuilder
from fitness.fitness_function import FitnessEvaluator
from ga.genetic_algorithm import GeneticAlgorithm


def create_test_data():
    """
    Generate a controlled test dataset for the GA solver.
    
    Returns:
        tuple: (timeslots, rooms, lecturers, student_groups, events)
               All as lists, plus dict versions for lookups.
    """
    # --- Timeslots: 5 days × 6 periods = 30 slots ---
    timeslots = []
    ts_id = 0
    for day in range(5):       # Mon–Fri
        for period in range(3): # 4 periods per day (e.g., 8am–2pm)
            timeslots.append(Timeslot(id=ts_id, day=day, period=period))
            ts_id += 1
    timeslots_dict = {t.id: t for t in timeslots}
    
    # --- Rooms ---
    rooms = [
        Room(id=0, capacity=30,  name="Room_A"),
        Room(id=1, capacity=50,  name="Room_B"),
        Room(id=2, capacity=70,  name="Room_C"),
        Room(id=3, capacity=100, name="Room_D"),
        Room(id=4, capacity=120, name="Lecture_Hall"),
    ]
    
    # --- Lecturers ---
    # Lecturer 0: unavailable Monday morning (periods 0,1)
    # Lecturer 1: unavailable Friday (periods 0-5 on day 4)
    # Lecturer 2: prefers mornings only (periods 0,1,2)
    # Lecturer 3: no constraints
    # Lecturer 4: unavailable Wednesday afternoon (day 2, periods 3,4,5)
    # Lecturer 5: prefers Tuesday/Thursday
    
    lecturers = [
        Lecturer(id=0, name="Dr. Ahmed",
                 unavailable_timeslots={0, 1},       # Mon periods 0,1
                 preferred_timeslots=set()),
        Lecturer(id=1, name="Dr. Baker",
                 unavailable_timeslots={24, 25, 26, 27, 28, 29},  # All Friday
                 preferred_timeslots=set()),
        Lecturer(id=2, name="Dr. Chen",
                 unavailable_timeslots=set(),
                 # Prefers periods 0,1,2 every day
                 preferred_timeslots={d * 4 + p for d in range(5) for p in range(3)}),
        Lecturer(id=3, name="Dr. Davis",
                 unavailable_timeslots=set(),
                 preferred_timeslots=set()),
        Lecturer(id=4, name="Dr. Evans",
                 unavailable_timeslots={15, 16, 17},  # Wed afternoon
                 preferred_timeslots=set()),
        Lecturer(id=5, name="Dr. Farah",
                 unavailable_timeslots=set(),
                 # Prefers Tue (day 1) and Thu (day 3) — all periods
                 preferred_timeslots={6,7,8,9,10,11, 18,19,20,21,22,23}),
    ]
    lecturers_dict = {l.id: l for l in lecturers}
    
    # --- Student Groups ---
    student_groups = [
        StudentGroup(id=0, name="CS_Y1_A", size=28),
        StudentGroup(id=1, name="CS_Y1_B", size=25),
        StudentGroup(id=2, name="CS_Y2_A", size=30),
    ]
    groups_dict = {g.id: g for g in student_groups}
    
    # --- Events ---
    # 25 events with realistic multi-group overlaps
    events = [
        # CS Year 1 courses — groups 0 and 1
        Event(id=0,  name="Intro to Programming",    lecturer_id=0, student_group_ids=[0, 1], size=53),
        Event(id=1,  name="Discrete Math",            lecturer_id=2, student_group_ids=[0, 1], size=53),
        Event(id=2,  name="CS Lab A",                 lecturer_id=0, student_group_ids=[0],    size=28),
        Event(id=3,  name="CS Lab B",                 lecturer_id=0, student_group_ids=[1],    size=25),
        
        # CS Year 2 courses — groups 2 and 3
        Event(id=4,  name="Data Structures",          lecturer_id=1, student_group_ids=[2, 3], size=57),
        Event(id=5,  name="Database Systems",         lecturer_id=3, student_group_ids=[2, 3], size=57),
        Event(id=6,  name="DS Lab A",                 lecturer_id=1, student_group_ids=[2],    size=30),
        Event(id=7,  name="DS Lab B",                 lecturer_id=1, student_group_ids=[3],    size=27),
        
        # Math Year 1 — group 4 (also serves CS Y1: overlap!)
        Event(id=8,  name="Calculus I",               lecturer_id=2, student_group_ids=[4, 0], size=73),
        Event(id=9,  name="Linear Algebra",           lecturer_id=2, student_group_ids=[4, 1], size=70),
        Event(id=10, name="Math Tutorial A",          lecturer_id=4, student_group_ids=[4],    size=45),
        
        # Math Year 2 — group 5 (overlap with CS Y2)
        Event(id=11, name="Calculus II",              lecturer_id=2, student_group_ids=[5, 2], size=70),
        Event(id=12, name="Probability & Stats",      lecturer_id=4, student_group_ids=[5, 3], size=67),
        Event(id=13, name="Math Tutorial B",          lecturer_id=4, student_group_ids=[5],    size=40),
        
        # Physics Year 1 — group 6 (overlap with Math Y1)
        Event(id=14, name="Physics I",                lecturer_id=3, student_group_ids=[6, 4], size=80),
        Event(id=15, name="Physics Lab",              lecturer_id=3, student_group_ids=[6],    size=35),
        Event(id=16, name="Mechanics",                lecturer_id=5, student_group_ids=[6],    size=35),
        
        # Physics Year 2 — group 7 (overlap with Math Y2)
        Event(id=17, name="Physics II",               lecturer_id=5, student_group_ids=[7, 5], size=72),
        Event(id=18, name="Electromagnetics",         lecturer_id=5, student_group_ids=[7],    size=32),
        Event(id=19, name="Physics Lab II",           lecturer_id=3, student_group_ids=[7],    size=32),
        
        # Cross-department shared events (high interaction density)
        Event(id=20, name="Intro to Statistics",      lecturer_id=4, student_group_ids=[0, 4, 6], size=108),
        Event(id=21, name="Scientific Computing",     lecturer_id=1, student_group_ids=[2, 5, 7], size=99),
        Event(id=22, name="Research Methods",         lecturer_id=3, student_group_ids=[3, 5],    size=67),
        Event(id=23, name="Technical Writing",        lecturer_id=0, student_group_ids=[2, 7],    size=62),
        Event(id=24, name="Seminar: AI Frontiers",    lecturer_id=1, student_group_ids=[0, 2],    size=58),
    ]
    events_dict = {e.id: e for e in events}
    
    return (timeslots, timeslots_dict, rooms,
            lecturers, lecturers_dict,
            student_groups, groups_dict,
            events, events_dict)


def print_timetable(timetable, events_dict, timeslots_dict, rooms):
    """
    Pretty-print the final timetable as a grid.
    """
    rooms_dict = {r.id: r for r in rooms}
    
    # Organize by day and period
    day_names = ["Sunday", "Monday", "Tuesday", "Wednesday", "Thursday"]
    
    # Build: (day, period) -> list of (event_name, room_name)
    from collections import defaultdict
    schedule_grid = defaultdict(list)
    
    for event_id, (ts_id, room_id) in timetable.items():
        event = events_dict[event_id]
        timeslot = timeslots_dict[ts_id]
        room = rooms_dict[room_id]
        schedule_grid[(timeslot.day, timeslot.period)].append(
            f"{event.name} [{room.name}] (Lecturer:{event.lecturer_id})"
        )
    
    print(f"\n{'='*80}")
    print(f"  FINAL TIMETABLE")
    print(f"{'='*80}")
    
    for day in range(5):
        print(f"\n--- {day_names[day]} ---")
        for period in range(6):
            entries = schedule_grid.get((day, period), [])
            if entries:
                print(f"  Period {period}:")
                for entry in entries:
                    print(f"    → {entry}")
            else:
                print(f"  Period {period}: [empty]")


def main():
    """Main execution."""
    # Set seed for reproducibility
    random.seed(42)
    
    # Create test data
    (timeslots, timeslots_dict, rooms,
     lecturers, lecturers_dict,
     student_groups, groups_dict,
     events, events_dict) = create_test_data()
    
    print(f"Problem Instance:")
    print(f"  Timeslots:      {len(timeslots)}")
    print(f"  Rooms:          {len(rooms)}")
    print(f"  Lecturers:      {len(lecturers)}")
    print(f"  Student Groups: {len(student_groups)}")
    print(f"  Events:         {len(events)}")
    print(f"  Search Space:   {len(timeslots)}×{len(rooms)} = "
          f"{len(timeslots) * len(rooms)} possible slots per event")
    print()
    
    # Create schedule builder (decoder)
    builder = ScheduleBuilder(
        timeslots=timeslots,
        rooms=rooms,
        lecturers_dict=lecturers_dict,
        events_dict=events_dict,
    )
    
    # Create fitness evaluator
    evaluator = FitnessEvaluator(
        timeslots_dict=timeslots_dict,
        events_dict=events_dict,
        lecturers_dict=lecturers_dict,
        alpha=10.0,    # Student gaps weight
        beta=5.0,      # Lecturer preference weight
        unplaced_penalty=100000.0,
    )
    
    # Event IDs for chromosome construction
    event_ids = [e.id for e in events]
    
    # Create and run GA
    ga = GeneticAlgorithm(
        schedule_builder=builder,
        fitness_evaluator=evaluator,
        event_ids=event_ids,
        population_size=100,
        generations=300,
        crossover_rate=0.85,
        mutation_rate=0.10,
        tournament_size=3,
        elitism_count=2,
    )
    
    best = ga.run()
    
    # Print the best timetable
    print_timetable(best['timetable'], events_dict, timeslots_dict, rooms)
    
    # Summary statistics
    print(f"\n{'='*80}")
    print(f"  SOLUTION SUMMARY")
    print(f"{'='*80}")
    print(f"  Total Fitness (lower=better):    {best['fitness']:.1f}")
    print(f"  Events Placed:                   "
          f"{len(best['timetable'])}/{len(events)}")
    print(f"  Events Unplaced:                 {best['unplaced_count']}")
    print(f"  Student Gap Violations (raw):    {best['student_gaps_raw']}")
    print(f"  Student Gap Penalty (weighted):  {best['student_gap_penalty']:.1f}")
    print(f"  Lecturer Pref Violations (raw):  {best['lecturer_violations_raw']}")
    print(f"  Lecturer Pref Penalty (weighted):{best['lecturer_pref_penalty']:.1f}")
    print(f"{'='*80}")


if __name__ == "__main__":
    main()