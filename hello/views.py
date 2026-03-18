"""Teacher Portal Views - Add to your existing views.py"""
from django.shortcuts import render, redirect
from django.contrib import messages
from datetime import date
import copy
import calendar as cal_module



#SAMPLE DATA

SAMPLE_UNITS = [
    {'id': 1, 'name': 'Digital Solutions - Year 12', 'code': '12001', 'status': 'DRAFT',
     'last_modified': date(2026, 2, 15), 'due_dates_info': 'items pending'},
    {'id': 2, 'name': 'Robotics - Year 12', 'code': '12003', 'status': 'PUBLISHED',
     'last_modified': date(2026, 2, 10), 'due_dates_info': '20 Feb 2026'},
]
_next_id = 3

SAMPLE_STUDENTS = [
    {'name': 'Emma Wilson', 'student_id': 'S12345', 'design_doc': 18, 'build1': 17, 'build2': 26, 'reflection': 18},
    {'name': 'Liam Chen', 'student_id': 'S12346', 'design_doc': 16, 'build1': 15, 'build2': 24, 'reflection': 16},
    {'name': 'Olivia Martinez', 'student_id': 'S12347', 'design_doc': 19, 'build1': 18, 'build2': 28, 'reflection': 19},
    {'name': 'Noah Thompson', 'student_id': 'S12348', 'design_doc': 14, 'build1': 13, 'build2': 20, 'reflection': 14},
    {'name': 'Sophia Anderson', 'student_id': 'S12349', 'design_doc': 17, 'build1': 16, 'build2': 25, 'reflection': None},
    {'name': 'Jackson Lee', 'student_id': 'S12350', 'design_doc': 15, 'build1': 14, 'build2': 22, 'reflection': 15},
    {'name': 'Ava Patel', 'student_id': 'S12351', 'design_doc': 18, 'build1': 17, 'build2': None, 'reflection': None},
    {'name': 'Ethan Brown', 'student_id': 'S12352', 'design_doc': 16, 'build1': 15, 'build2': 23, 'reflection': 16},
]

# Assessment con = max marks
ASSESSMENTS = [
    ('design_doc', 20, 0.20),
    ('build1', 20, 0.20),
    ('build2', 30, 0.30),
    ('reflection', 20, 0.20),
]



# FUNCTIONS

def calc_grade(student):
    """Calculate percentage and letter grade. Returns (pct, letter) or (None, None)."""
    for key, max_m, _ in ASSESSMENTS:
        if student.get(key) is None:
            return None, None
    
    total = sum((student[k] / m) * w for k, m, w in ASSESSMENTS) * 100
    pct = round(total)
    
    if pct >= 85: letter = 'A'
    elif pct >= 70: letter = 'B'
    elif pct >= 55: letter = 'C'
    elif pct >= 40: letter = 'D'
    else: letter = 'F'
    
    return pct, letter


def add_grades(students):
    """Add grade_pct and grade_letter to each student."""
    for s in students:
        s['grade_pct'], s['grade_letter'] = calc_grade(s)
    return students



# VIEW FUNCTIONS

def dashboard(request):
    """Main dashboard with unit outlines and deadlines."""
    deadlines = [
        {'assessment_item': 'Design Document', 'unit': 'Digital Solutions Y12',
         'due_date': date(2026, 2, 20), 'status': 'Outline Pending'},
        {'assessment_item': 'Build 1', 'unit': 'Digital Solutions Y12',
         'due_date': date(2026, 3, 20), 'status': 'Outline Pending'},
    ]
    return render(request, 'dashboard.html', {
        'user_name': 'Teacher',
        'recent_units': SAMPLE_UNITS,
        'upcoming_deadlines': deadlines,
    })


def unit_outline(request):
    """Unit outline editor."""
    unit = {'code': '12001', 'title': 'Digital Solutions', 'year_level': 'Year 12'}
    items = [
        {'name': 'Design Document', 'weighting': '30%', 'start_date': '27/01/2026', 'due_date': '26/02/2026'},
        {'name': 'Build 1', 'weighting': '20%', 'start_date': '21/02/2026', 'due_date': '20/03/2026'},
        {'name': 'Build 2', 'weighting': '30%', 'start_date': '30/03/2026', 'due_date': '22/05/2026'},
        {'name': 'Reflection', 'weighting': '20%', 'start_date': '25/05/2026', 'due_date': '12/06/2026'},
    ]
    return render(request, 'unit_outline.html', {'unit': unit, 'assessment_items': items})


def markbook(request):
    """Markbook with student grades."""
    students = add_grades(copy.deepcopy(SAMPLE_STUDENTS))
    graded = [s for s in students if s['grade_pct']]
    avg = round(sum(s['grade_pct'] for s in graded) / len(graded)) if graded else 0
    
    return render(request, 'markbook.html', {
        'unit': {'code': '12001', 'title': 'Digital Solutions', 'year_level': 'Year 12',
                 'teacher': 'Ms. Johnson', 'semester': 'Semester 1, 2026'},
        'stats': {'total_students': len(students), 'completed_assessments': len(graded),
                  'pending_marks': len(students) - len(graded), 'class_average': avg},
        'students': students,
    })


def update_grade(request):
    """Update a single grade via POST."""
    if request.method != 'POST':
        return redirect('teacher_portal:markbook')
    
    sid = request.POST.get('student_id')
    assess = request.POST.get('assessment')
    mark_str = request.POST.get('mark', '')
    
    # Find max marks for this assessment
    max_marks = {k: m for k, m, _ in ASSESSMENTS}.get(assess, 20)
    
    try:
        mark = int(mark_str)
        if mark < 0 or mark > max_marks:
            raise ValueError
    except ValueError:
        messages.error(request, f'Mark must be 0-{max_marks}')
        return redirect('teacher_portal:markbook')
    
    # Update student
    for s in SAMPLE_STUDENTS:
        if s['student_id'] == sid:
            s[assess] = mark
            messages.success(request, f'Updated {s["name"]} - {assess}: {mark}/{max_marks}')
            break
    
    return redirect('teacher_portal:markbook')


def calendar_view(request):
    """Calendar view."""
    year, month = 2026, 3
    events = {
        20: [{'label': 'Build 1 Due', 'type': 'deadline'}],
        27: [{'label': 'Term 1 Ends', 'type': 'term'}],
        30: [{'label': 'Build 2 Start', 'type': 'start'}],
    }
    
    cal = cal_module.Calendar(firstweekday=0)
    today = date.today()
    weeks = []
    for week in cal.monthdayscalendar(year, month):
        week_data = []
        for day in week:
            week_data.append({
                'number': day if day else '',
                'other_month': day == 0,
                'is_today': day and today == date(year, month, day),
                'events': events.get(day, []),
            })
        weeks.append(week_data)
    
    return render(request, 'calendar.html', {
        'month_name': 'March', 'year': year, 'calendar_weeks': weeks,
    })


def clone_unit_action(request):
    """Clone a unit outline."""
    global _next_id
    
    if request.method != 'POST':
        return redirect('teacher_portal:dashboard')
    
    unit_id = request.POST.get('unit_id')
    original = next((u for u in SAMPLE_UNITS if str(u['id']) == unit_id), None)
    
    if not original:
        messages.error(request, 'Unit not found')
        return redirect('teacher_portal:dashboard')
    
    # Create clone
    clone = copy.deepcopy(original)
    clone['id'] = _next_id
    _next_id += 1
    clone['name'] = f"Copy of {original['name']}"
    clone['status'] = 'DRAFT'
    clone['last_modified'] = date.today()
    
    SAMPLE_UNITS.insert(0, clone)
    messages.success(request, f'Cloned "{original["name"]}"')
    
    return redirect('teacher_portal:dashboard')