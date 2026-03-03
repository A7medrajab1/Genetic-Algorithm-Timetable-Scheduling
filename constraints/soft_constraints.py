"""
Soft Constraint Evaluation Module (v3)

Implements four soft constraints:
    S1a — Minimize Student Gaps (idle periods between events)
    S1b — Penalize Single-Event Days (coming to campus for 1 class)
    S4  — Promote Event Spreading (penalize overloaded days)
    S5  — Lecturer Time Preferences
"""

from collections import defaultdict
import math


def calculate_student_gap_penalty(timetable, timeslots_dict, events_dict):
    """
    S1a: Minimize idle gaps in each student group's daily schedule.
    
    For each student group, for each day:
        Find all periods with events.
        Count empty periods between first and last event.
    
    Example:
        Periods with events: [0, 2]  (08:00 and 12:00)
        Gap: period 1 (10:00) is empty between them
        Penalty: 1 gap
    
    Returns:
        int: Total gap count across all groups and all days.
    """
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
                continue
            
            sorted_periods = sorted(periods)
            span = sorted_periods[-1] - sorted_periods[0] + 1
            gaps = span - len(sorted_periods)
            total_gaps += gaps
    
    return total_gaps


def calculate_single_event_day_penalty(timetable, timeslots_dict, events_dict):
    """
    S1b: Penalize days where a student group has only ONE event.
    
    Coming to campus for a single 2-hour class is wasteful.
    Students prefer either a free day or multiple classes.
    
    Returns:
        int: Total count of single-event days across all groups.
    """
    group_day_counts = defaultdict(lambda: defaultdict(int))
    
    for event_id, (timeslot_id, room_id) in timetable.items():
        event = events_dict[event_id]
        timeslot = timeslots_dict[timeslot_id]
        
        for group_id in event.student_group_ids:
            group_day_counts[group_id][timeslot.day] += 1
    
    total_single_days = 0
    
    for group_id, day_counts in group_day_counts.items():
        for day, count in day_counts.items():
            if count == 1:
                total_single_days += 1
    
    return total_single_days


def calculate_spreading_penalty(timetable, timeslots_dict, events_dict):
    """
    S4: Penalize uneven distribution of events across the week.
    
    For each student group:
        Count events per day.
        Penalize any day with MORE than 3 events (overloaded).
        The penalty grows quadratically (3 events over = penalty 1,
        but 4 events = penalty 4, to strongly discourage extreme clustering).
    
    Also penalize if events use fewer than half the available days
    (e.g., all events crammed into 2 out of 6 days).
    
    Returns:
        int: Total spreading penalty.
    """
    group_day_counts = defaultdict(lambda: defaultdict(int))
    group_total_events = defaultdict(int)
    
    for event_id, (timeslot_id, room_id) in timetable.items():
        event = events_dict[event_id]
        timeslot = timeslots_dict[timeslot_id]
        
        for group_id in event.student_group_ids:
            group_day_counts[group_id][timeslot.day] += 1
            group_total_events[group_id] += 1
    
    total_penalty = 0
    
    # Get total available days
    all_days = set(ts.day for ts in timeslots_dict.values())
    num_available_days = len(all_days)
    
    for group_id, day_counts in group_day_counts.items():
        total_events = group_total_events[group_id]
        num_active_days = len(day_counts)
        
        # Penalty 1: Overloaded days (more than 3 events in one day)
        # With 3 periods per day, having all 3 full is the max
        # Penalize if any day is completely full (3 events)
        # when the group has enough events to spread more
        max_acceptable = 3 if total_events > num_available_days * 2 else 2
        
        for day, count in day_counts.items():
            if count > max_acceptable:
                excess = count - max_acceptable
                total_penalty += excess * excess  # Quadratic penalty
        
        # Penalty 2: Too few active days
        # If group has 7+ events but only uses 3 days, that's bad
        min_desired_days = min(
            num_available_days,
            math.ceil(total_events / 2)  # At most 2 events per day ideal
        )
        
        if num_active_days < min_desired_days:
            day_deficit = min_desired_days - num_active_days
            total_penalty += day_deficit * 2
    
    return total_penalty


def calculate_lecturer_preference_penalty(timetable, timeslots_dict,
                                           events_dict, lecturers_dict):
    """
    S5: Penalize events scheduled outside lecturer's preferred timeslots.
    
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