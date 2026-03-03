"""
Main Entry Point — UCTP Genetic Algorithm Solver

Faculty of Computer Science — 4 Academic Years

Schedule Structure:
    Days:    Saturday through Thursday (6 days)
    Periods: 3 per day, each 2 hours (08:00-14:00)
    Total:   18 timeslots

Problem Instance:
    - 18 timeslots (6 days x 3 periods)
    - 5 rooms
    - 8 lecturers
    - 4 student groups (CS Year 1-4)
    - 28 events (24 department + 4 shared)
"""

import random
from collections import defaultdict

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
    Generate dataset for Faculty of Computer Science.

    Timeslot ID Map (6 days x 3 periods = 18 slots):

        Day/Period     P0(08-10)  P1(10-12)  P2(12-14)
        Saturday       0          1          2
        Sunday         3          4          5
        Monday         6          7          8
        Tuesday        9          10         11
        Wednesday      12         13         14
        Thursday       15         16         17

    Student Groups:
        0: CS_Y1 (70 students) — First Year
        1: CS_Y2 (60 students) — Second Year
        2: CS_Y3 (50 students) — Third Year
        3: CS_Y4 (40 students) — Fourth Year

    Shared Course Conflict Map:
        Linear Algebra      → Y1 + Y2 (130 students)
        Probability & Stats → Y2 + Y3 (110 students)
        Technical Writing   → Y3 + Y4 (90 students)
        Research Methods    → Y3 + Y4 (90 students)

    Lecturer Assignment:
        L0: Dr. Ahmed    — Programming, OOP, Lab I, Lab II
        L1: Dr. Baker    — Data Structures, Algorithms, Machine Learning
        L2: Dr. Chen     — Calculus I, Calculus II, Linear Algebra, Prob&Stats
        L3: Dr. Davis    — Digital Logic, Computer Architecture, Compiler Design
        L4: Dr. Evans    — Database Systems, Distributed Systems, Info Security
        L5: Dr. Farah    — OS, Networks, Graduation Project I
        L6: Dr. Ghali    — Discrete Math, AI, Software Engineering
        L7: Dr. Hassan   — Physics, Technical Writing, Research Methods, Labs
    """

    # =================================================================
    #  TIMESLOTS: 6 days x 3 periods = 18 slots
    # =================================================================
    timeslots = []
    ts_id = 0
    for day in range(6):
        for period in range(3):
            timeslots.append(Timeslot(id=ts_id, day=day, period=period))
            ts_id += 1
    timeslots_dict = {t.id: t for t in timeslots}

    # =================================================================
    #  ROOMS: 5 rooms
    #
    #  Capacity audit:
    #    Largest single-group event: 70 (Y1 courses) → needs Room_C
    #    Largest shared event: Linear Algebra = 130 → needs Lecture_Hall
    #    All Y4 courses: 40 → fits Room_A
    # =================================================================
    rooms = [
        Room(id=0, capacity=45,  name="Lab_Room"),
        Room(id=1, capacity=65,  name="Room_B"),
        Room(id=2, capacity=80,  name="Room_C"),
        Room(id=3, capacity=120, name="Room_D"),
        Room(id=4, capacity=150, name="Lecture_Hall"),
    ]

    # =================================================================
    #  LECTURERS: 8 lecturers
    #
    #  Slot IDs:
    #    Sat:0,1,2 | Sun:3,4,5 | Mon:6,7,8
    #    Tue:9,10,11 | Wed:12,13,14 | Thu:15,16,17
    # =================================================================
    lecturers = [
        Lecturer(
            id=0, name="Dr. Ahmed",
            # Unavailable: Saturday 08:00 (slot 0)
            unavailable_timeslots={0},
            preferred_timeslots=set()
        ),
        Lecturer(
            id=1, name="Dr. Baker",
            # Unavailable: All Thursday
            unavailable_timeslots={15, 16, 17},
            preferred_timeslots=set()
        ),
        Lecturer(
            id=2, name="Dr. Chen",
            unavailable_timeslots=set(),
            # Prefers mornings only (period 0 every day)
            preferred_timeslots={0, 3, 6, 9, 12, 15}
        ),
        Lecturer(
            id=3, name="Dr. Davis",
            # Unavailable: Wednesday afternoon (slot 14)
            unavailable_timeslots={14},
            preferred_timeslots=set()
        ),
        Lecturer(
            id=4, name="Dr. Evans",
            unavailable_timeslots=set(),
            # Prefers Sunday and Tuesday
            preferred_timeslots={3, 4, 5, 9, 10, 11}
        ),
        Lecturer(
            id=5, name="Dr. Farah",
            # Unavailable: Saturday (all slots)
            unavailable_timeslots={0, 1, 2},
            preferred_timeslots=set()
        ),
        Lecturer(
            id=6, name="Dr. Ghali",
            unavailable_timeslots=set(),
            # Prefers mornings (period 0) and mid-day (period 1)
            preferred_timeslots={
                0, 1, 3, 4, 6, 7, 9, 10, 12, 13, 15, 16
            }
        ),
        Lecturer(
            id=7, name="Dr. Hassan",
            # Unavailable: Thursday afternoon (slots 16, 17)
            unavailable_timeslots={16, 17},
            # Prefers Monday and Wednesday
            preferred_timeslots={6, 7, 8, 12, 13, 14}
        ),
    ]
    lecturers_dict = {l.id: l for l in lecturers}

    # =================================================================
    #  STUDENT GROUPS: 4 groups (CS Year 1 through Year 4)
    #
    #  ID  Name    Size  Year
    #  0   CS_Y1   70    First Year
    #  1   CS_Y2   60    Second Year
    #  2   CS_Y3   50    Third Year
    #  3   CS_Y4   40    Fourth Year
    # =================================================================
    student_groups = [
        StudentGroup(id=0, name="CS_Y1", size=70),
        StudentGroup(id=1, name="CS_Y2", size=60),
        StudentGroup(id=2, name="CS_Y3", size=50),
        StudentGroup(id=3, name="CS_Y4", size=40),
    ]
    groups_dict = {g.id: g for g in student_groups}

    # =================================================================
    #  EVENTS: 28 total (24 department + 4 shared)
    #
    #  Year 1 (group 0): 6 courses — Foundation
    #  Year 2 (group 1): 6 courses — Core
    #  Year 3 (group 2): 6 courses — Advanced
    #  Year 4 (group 3): 6 courses — Specialization
    #  Shared:           4 courses — Cross-year
    #
    #  Conflict Map:
    #    CS_Y1(0) ─── Linear Algebra ─── CS_Y2(1)
    #    CS_Y2(1) ─── Prob & Stats ───── CS_Y3(2)
    #    CS_Y3(2) ─── Tech Writing ───── CS_Y4(3)
    #    CS_Y3(2) ─── Research Methods ─ CS_Y4(3)
    # =================================================================
    events = [
        # ─── YEAR 1: Foundation (group 0) ───
        Event(id=0,  name="Intro to Programming",
              lecturer_id=0, student_group_ids=[0]),
        Event(id=1,  name="Discrete Math",
              lecturer_id=6, student_group_ids=[0]),
        Event(id=2,  name="Calculus I",
              lecturer_id=2, student_group_ids=[0]),
        Event(id=3,  name="Physics for CS",
              lecturer_id=7, student_group_ids=[0]),
        Event(id=4,  name="Digital Logic",
              lecturer_id=3, student_group_ids=[0]),
        Event(id=5,  name="CS Lab I",
              lecturer_id=0, student_group_ids=[0]),

        # ─── YEAR 2: Core (group 1) ───
        Event(id=6,  name="Data Structures",
              lecturer_id=1, student_group_ids=[1]),
        Event(id=7,  name="OOP",
              lecturer_id=0, student_group_ids=[1]),
        Event(id=8,  name="Database Systems",
              lecturer_id=4, student_group_ids=[1]),
        Event(id=9,  name="Calculus II",
              lecturer_id=2, student_group_ids=[1]),
        Event(id=10, name="Computer Architecture",
              lecturer_id=3, student_group_ids=[1]),
        Event(id=11, name="CS Lab II",
              lecturer_id=0, student_group_ids=[1]),

        # ─── YEAR 3: Advanced (group 2) ───
        Event(id=12, name="Operating Systems",
              lecturer_id=5, student_group_ids=[2]),
        Event(id=13, name="Computer Networks",
              lecturer_id=5, student_group_ids=[2]),
        Event(id=14, name="Software Engineering",
              lecturer_id=6, student_group_ids=[2]),
        Event(id=15, name="Algorithms",
              lecturer_id=1, student_group_ids=[2]),
        Event(id=17, name="CS Lab III",
              lecturer_id=7, student_group_ids=[2]),

        # ─── YEAR 4: Specialization (group 3) ───
        Event(id=20, name="Information Security",
              lecturer_id=4, student_group_ids=[3]),
        Event(id=21, name="Graduation Project I",
              lecturer_id=5, student_group_ids=[3]),
        Event(id=23, name="CS Lab IV",
              lecturer_id=7, student_group_ids=[3]),

        # ─── SHARED: Year 3 + Year 4 ───
        Event(id=16, name="Artificial Intelligence",
              lecturer_id=6, student_group_ids=[2, 3]),
        Event(id=18, name="Machine Learning",
              lecturer_id=1, student_group_ids=[3, 2]),
        Event(id=19, name="Distributed Systems",
              lecturer_id=4, student_group_ids=[3, 2]),
        Event(id=22, name="Compiler Design",
              lecturer_id=3, student_group_ids=[3, 2]),

        # ─── SHARED: Cross-Year ───
        # Y1 + Y2
        Event(id=24, name="Linear Algebra",
              lecturer_id=2, student_group_ids=[0, 1]),

        # Y2 + Y3
        Event(id=25, name="Probability & Stats",
              lecturer_id=2, student_group_ids=[1, 2]),

        # Y3 + Y4
        Event(id=26, name="Technical Writing",
              lecturer_id=7, student_group_ids=[2, 3]),

        # Y3 + Y4
        Event(id=27, name="Research Methods",
              lecturer_id=7, student_group_ids=[2, 3]),
    ]

    # =================================================================
    #  CALCULATE SIZES DYNAMICALLY
    # =================================================================
    for event in events:
        event.calculate_size(groups_dict)

    events_dict = {e.id: e for e in events}

    # Print size verification
    print(f"\n  {'─'*60}")
    print(f"  DYNAMIC SIZE CALCULATION:")
    print(f"  {'─'*60}")
    for event in sorted(events, key=lambda e: e.size, reverse=True):
        group_names = [groups_dict[gid].name for gid in event.student_group_ids]
        group_sizes = [str(groups_dict[gid].size) for gid in event.student_group_ids]
        size_formula = " + ".join(group_sizes)
        print(f"    {event.name:<25s} "
              f"Groups: {', '.join(group_names):<20s} "
              f"Size: {size_formula} = {event.size}")

    # =================================================================
    #  Print conflict analysis
    # =================================================================
    print(f"  {'─'*60}")
    print(f"  FACULTY OF COMPUTER SCIENCE — CONFLICT ANALYSIS")
    print(f"  {'─'*60}")

    # Events per group
    for group in student_groups:
        group_events = [e for e in events
                        if group.id in e.student_group_ids]
        print(f"\n  {group.name} ({group.size} students) "
              f"— {len(group_events)} events:")
        for e in group_events:
            shared = " [SHARED]" if len(e.student_group_ids) > 1 else ""
            lec = lecturers_dict[e.lecturer_id].name
            print(f"      {e.name:<25s} ({lec}){shared}")

    # Shared events
    shared = [e for e in events if len(e.student_group_ids) > 1]
    print(f"\n  {'─'*60}")
    print(f"  SHARED COURSES (create scheduling conflicts): {len(shared)}")
    print(f"  {'─'*60}")
    for e in shared:
        group_names = [groups_dict[gid].name
                       for gid in e.student_group_ids]
        lec = lecturers_dict[e.lecturer_id].name
        print(f"    {e.name:<25s} → {', '.join(group_names):<20s} "
              f"(size={e.size}, {lec})")

    # Lecturer workload
    print(f"\n  {'─'*60}")
    print(f"  LECTURER WORKLOAD:")
    print(f"  {'─'*60}")
    for lec in lecturers:
        lec_events = [e for e in events if e.lecturer_id == lec.id]
        event_names = [e.name[:20] for e in lec_events]
        unavail = (f"Unavailable: {lec.unavailable_timeslots}"
                   if lec.unavailable_timeslots else "")
        pref = (f"Preferred: {lec.preferred_timeslots}"
                if lec.preferred_timeslots else "")
        print(f"    {lec.name:<15s}: {len(lec_events)} events  "
              f"{unavail}  {pref}")
        for name in event_names:
            print(f"        - {name}")

    # Room capacity check
    print(f"\n  {'─'*60}")
    print(f"  ROOM CAPACITY CHECK:")
    print(f"  {'─'*60}")
    for e in sorted(events, key=lambda x: x.size, reverse=True):
        fitting_rooms = [r for r in rooms if r.capacity >= e.size]
        room_names = [r.name for r in fitting_rooms]
        status = "OK" if fitting_rooms else "IMPOSSIBLE"
        print(f"    {e.name:<25s} size={e.size:>3d} → "
              f"fits in: {', '.join(room_names):<40s} [{status}]")

    print(f"  {'─'*60}")

    return (timeslots, timeslots_dict, rooms,
            lecturers, lecturers_dict,
            student_groups, groups_dict,
            events, events_dict)


def print_timetable(timetable, events_dict, timeslots_dict, rooms):
    """Pretty-print the final timetable."""
    rooms_dict = {r.id: r for r in rooms}

    schedule_grid = defaultdict(list)

    for event_id, (ts_id, room_id) in timetable.items():
        event = events_dict[event_id]
        timeslot = timeslots_dict[ts_id]
        room = rooms_dict[room_id]
        groups_str = ",".join(str(g) for g in event.student_group_ids)
        lec_id = event.lecturer_id
        schedule_grid[(timeslot.day, timeslot.period)].append(
            f"{event.name:<25s} [{room.name:<12s}] "
            f"(Lecturer:{lec_id}, Groups:[{groups_str}], Size:{event.size})"
        )

    print(f"\n{'='*95}")
    print(f"  FINAL TIMETABLE — Faculty of Computer Science")
    print(f"  Saturday-Thursday | 08:00-10:00 / 10:00-12:00 / 12:00-14:00")
    print(f"{'='*95}")

    period_labels = ["08:00-10:00", "10:00-12:00", "12:00-14:00"]

    for day in range(6):
        day_name = Timeslot.DAY_NAMES[day]
        print(f"\n{'─'*95}")
        print(f"  {day_name.upper()}")
        print(f"{'─'*95}")
        for period in range(3):
            entries = schedule_grid.get((day, period), [])
            if entries:
                print(f"  {period_labels[period]}:")
                for entry in entries:
                    print(f"    -> {entry}")
            else:
                print(f"  {period_labels[period]}: [empty]")


def print_group_schedules(timetable, events_dict, timeslots_dict,
                           student_groups):
    """Print each year's weekly schedule."""

    period_labels = ["08-10", "10-12", "12-14"]

    group_schedules = defaultdict(lambda: defaultdict(list))

    for event_id, (ts_id, room_id) in timetable.items():
        event = events_dict[event_id]
        timeslot = timeslots_dict[ts_id]
        for gid in event.student_group_ids:
            group_schedules[gid][(timeslot.day, timeslot.period)].append(
                event.name
            )

    print(f"\n{'='*90}")
    print(f"  STUDENT YEAR SCHEDULES")
    print(f"{'='*90}")

    for group in student_groups:
        schedule = group_schedules[group.id]
        total_events = sum(len(v) for v in schedule.values())

        # Count gaps
        total_gaps = 0
        for day in range(6):
            day_periods = []
            for period in range(3):
                if schedule.get((day, period), []):
                    day_periods.append(period)
            if len(day_periods) >= 2:
                first = min(day_periods)
                last = max(day_periods)
                span = last - first + 1
                gaps = span - len(day_periods)
                total_gaps += gaps

        print(f"\n  {group.name} ({group.size} students, "
              f"{total_events} events/week, "
              f"{total_gaps} gaps)")
        print(f"  {'─'*65}")

        for day in range(6):
            day_name = Timeslot.DAY_NAMES[day][:3]
            day_events = []
            for period in range(3):
                entries = schedule.get((day, period), [])
                if entries:
                    names = ', '.join(e[:18] for e in entries)
                    day_events.append(f"{period_labels[period]}: {names}")

            if day_events:
                print(f"    {day_name}: {' | '.join(day_events)}")
            else:
                print(f"    {day_name}: [free day]")


def print_lecturer_schedules(timetable, events_dict, timeslots_dict,
                              lecturers):
    """Print each lecturer's weekly teaching schedule."""

    period_labels = ["08-10", "10-12", "12-14"]

    lecturer_schedules = defaultdict(lambda: defaultdict(list))

    for event_id, (ts_id, room_id) in timetable.items():
        event = events_dict[event_id]
        timeslot = timeslots_dict[ts_id]
        lecturer_schedules[event.lecturer_id][
            (timeslot.day, timeslot.period)
        ].append(event.name)

    print(f"\n{'='*90}")
    print(f"  LECTURER SCHEDULES")
    print(f"{'='*90}")

    for lecturer in lecturers:
        schedule = lecturer_schedules[lecturer.id]
        event_count = sum(len(v) for v in schedule.values())

        # Count preference violations
        pref_violations = 0
        if lecturer.preferred_timeslots:
            for event_id, (ts_id, room_id) in timetable.items():
                event = events_dict[event_id]
                if (event.lecturer_id == lecturer.id and
                        ts_id not in lecturer.preferred_timeslots):
                    pref_violations += 1

        print(f"\n  {lecturer.name} (ID:{lecturer.id}) — "
              f"{event_count} events/week"
              f"{f', {pref_violations} pref violations' if pref_violations else ''}")

        if lecturer.unavailable_timeslots:
            print(f"    Unavailable: slots {lecturer.unavailable_timeslots}")
        if lecturer.preferred_timeslots:
            print(f"    Preferred:   slots {lecturer.preferred_timeslots}")

        print(f"  {'─'*60}")

        for day in range(6):
            day_name = Timeslot.DAY_NAMES[day][:3]
            day_events = []
            for period in range(3):
                entries = schedule.get((day, period), [])
                if entries:
                    names = ', '.join(e[:20] for e in entries)
                    day_events.append(f"{period_labels[period]}: {names}")

            if day_events:
                print(f"    {day_name}: {' | '.join(day_events)}")


def main():
    """Main execution."""
    random.seed(42)

    # Create test data
    (timeslots, timeslots_dict, rooms,
     lecturers, lecturers_dict,
     student_groups, groups_dict,
     events, events_dict) = create_test_data()

    print(f"\n{'='*70}")
    print(f"  UCTP Problem Instance — Faculty of Computer Science")
    print(f"{'='*70}")
    print(f"  Days:            Saturday - Thursday (6 days)")
    print(f"  Periods/Day:     3 (08:00-10:00, 10:00-12:00, 12:00-14:00)")
    print(f"  Timeslots:       {len(timeslots)} (6 x 3)")
    print(f"  Rooms:           {len(rooms)}")
    print(f"  Lecturers:       {len(lecturers)}")
    print(f"  Student Years:   {len(student_groups)}")
    print(f"  Events:          {len(events)}")
    print(f"  Slot Capacity:   {len(timeslots) * len(rooms)} "
          f"(timeslots x rooms)")
    print(f"  Load Factor:     "
          f"{len(events) / (len(timeslots) * len(rooms)) * 100:.1f}%")

    # Events per year
    for g in student_groups:
        count = sum(1 for e in events if g.id in e.student_group_ids)
        print(f"    {g.name}: {count} events "
              f"({count} of {len(timeslots)} slots used = "
              f"{count/len(timeslots)*100:.0f}%)")
    print()

    # Create schedule builder
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
        alpha=10.0,
        beta=5.0,
        gamma=8.0,
        unplaced_penalty=100000.0,
    )

    event_ids = [e.id for e in events]

    # Create and run GA
    ga = GeneticAlgorithm(
        schedule_builder=builder,
        fitness_evaluator=evaluator,
        event_ids=event_ids,
        population_size=150,
        generations=500,
        crossover_rate=0.85,
        swap_mutation_rate=0.15,
        inversion_mutation_rate=0.08,
        tournament_size=4,
        elitism_count=3,
    )

    best = ga.run()

    # Print all results
    print_timetable(best['timetable'], events_dict, timeslots_dict, rooms)
    print_group_schedules(best['timetable'], events_dict, timeslots_dict,
                          student_groups)
    print_lecturer_schedules(best['timetable'], events_dict, timeslots_dict,
                             lecturers)

    # Summary
    print(f"\n{'='*70}")
    print(f"  SOLUTION SUMMARY")
    print(f"{'='*70}")
    print(f"  Total Fitness (lower=better):     {best['fitness']:.1f}")
    print(f"  Events Placed:                    "
          f"{len(best['timetable'])}/{len(events)}")
    print(f"  Events Unplaced:                  {best['unplaced_count']}")
    print(f"  {'─'*50}")
    print(f"  Student Gap Violations (raw):     {best['student_gaps_raw']}")
    print(f"  Student Gap Penalty (x{evaluator.alpha}):      "
          f"{best['student_gap_penalty']:.1f}")
    print(f"  {'─'*50}")
    print(f"  Spreading Violations (raw):       {best['spreading_raw']}")
    print(f"  Spreading Penalty (x{evaluator.gamma}):       "
          f"{best['spreading_penalty']:.1f}")
    print(f"  {'─'*50}")
    print(f"  Lecturer Pref Violations (raw):   "
          f"{best['lecturer_violations_raw']}")
    print(f"  Lecturer Pref Penalty (x{evaluator.beta}):    "
          f"{best['lecturer_pref_penalty']:.1f}")
    print(f"{'='*70}")


if __name__ == "__main__":
    main()