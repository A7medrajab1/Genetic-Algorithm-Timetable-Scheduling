"""
Soft Constraint Evaluation Module

Implements the two soft constraints from the scoped problem:
    S1a — Minimize Student Gaps (idle periods between events in a day)
    S5  — Lecturer Time Preferences

These operate on a COMPLETE, DECODED timetable and return penalty values.
"""

from collections import defaultdict


def calculate_student_gap_penalty(timetable, timeslots_dict, events_dict):
    """
    S1a: Minimize idle gaps in each student group's daily schedule.
    
    For each student group, for each day:
        1. Find all periods where they have events.
        2. Count the idle (empty) periods between the first and last event.
    
    Args:
        timetable: dict mapping event_id -> (timeslot_id, room_id).
        timeslots_dict: dict mapping timeslot_id -> Timeslot object.
        events_dict: dict mapping event_id -> Event object.
    
    Returns:
        int: Total gap count across all student groups and all days.
    """
    # Build: student_group_id -> day -> sorted list of periods
    group_day_periods = defaultdict(lambda: defaultdict(list))
    
    for event_id, (timeslot_id, room_id) in timetable.items():
        event = events_dict[event_id]
        timeslot = timeslots_dict[timeslot_id]
        
        for group_id in event.student_group_ids:
            group_day_periods[group_id][timeslot.day].append(timeslot.period)
    
    total_gaps = 0
    
    for group_id, days in group_day_periods.items():
        for day, periods in days.items():
            if len(periods) <= 1:
                continue  # No gap possible with 0 or 1 event
            
            sorted_periods = sorted(periods)
            first = sorted_periods[0]
            last = sorted_periods[-1]
            
            # Total slots in the span minus actual events = gaps
            span = last - first + 1
            events_in_span = len(sorted_periods)
            gaps = span - events_in_span
            
            total_gaps += gaps
    
    return total_gaps


def calculate_lecturer_preference_penalty(timetable, timeslots_dict,
                                           events_dict, lecturers_dict):
    """
    S5: Penalize events scheduled outside lecturer's preferred timeslots.
    
    For each event in the timetable:
        If the lecturer has specified preferred timeslots,
        and the assigned timeslot is NOT in that set, add 1 penalty.
    
    Args:
        timetable: dict mapping event_id -> (timeslot_id, room_id).
        timeslots_dict: dict mapping timeslot_id -> Timeslot object.
        events_dict: dict mapping event_id -> Event object.
        lecturers_dict: dict mapping lecturer_id -> Lecturer object.
    
    Returns:
        int: Total count of lecturer preference violations.
    """
    total_violations = 0
    
    for event_id, (timeslot_id, room_id) in timetable.items():
        event = events_dict[event_id]
        lecturer = lecturers_dict.get(event.lecturer_id)
        
        if lecturer is None:
            continue
        
        if not lecturer.prefers(timeslot_id):
            total_violations += 1
    
    return total_violations