from typing_extensions import Buffer

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.http import FileResponse
from datetime import date
from io import BytesIO
import calendar as cal_module

from reportlab.pdfgen import canvas
from reportlab.platypus import Table
from pypdf import PdfWriter, PdfReader

from .models import UnitOutline, AssessmentItem
from .forms import UnitOutlineForm, AssessmentFormSet


MONTH_NAMES = ['', 'January', 'February', 'March', 'April', 'May', 'June',
               'July', 'August', 'September', 'October', 'November', 'December']


def dashboard(request):
    # Home page list units + show next 10 upcoming assessments
    units = UnitOutline.objects.all()
    today = date.today()
    upcoming = (AssessmentItem.objects
                .filter(due_date__gte=today)
                .select_related('unit')
                .order_by('due_date')[:10])
    return render(request, 'dashboard.html', {
        'units': units,
        'upcoming': upcoming,
    })


def unit_list(request):
    # Plain table of all units
    return render(request, 'unit_list.html', {'units': UnitOutline.objects.all()})


def unit_edit(request, pk=None):
    # Create or edit one unit plus its assessment rows
    unit = get_object_or_404(UnitOutline, pk=pk) if pk else None
    if request.method == 'POST':
        form = UnitOutlineForm(request.POST, request.FILES, instance=unit)
        if form.is_valid():
            saved_unit = form.save()
            formset = AssessmentFormSet(request.POST, instance=saved_unit)
            if formset.is_valid():
                formset.save()
                messages.success(request, f'Saved "{saved_unit.name}".')
                return redirect('teacher_portal:unit_edit', pk=saved_unit.pk)
        else:
            formset = AssessmentFormSet(request.POST, instance=unit)
    else:
        form = UnitOutlineForm(instance=unit)
        formset = AssessmentFormSet(instance=unit)
    return render(request, 'unit_edit.html',
                  {'form': form, 'formset': formset, 'unit': unit})


def unit_delete(request, pk):
    # Confirm-then-delete a unit
    unit = get_object_or_404(UnitOutline, pk=pk)
    if request.method == 'POST':
        name = unit.name
        unit.delete()
        messages.success(request, f'Deleted "{name}".')
        return redirect('teacher_portal:dashboard')
    return render(request, 'unit_confirm_delete.html', {'unit': unit})


def unit_clone(request, pk):
    # Copy a unit and all its assessments as a new DRAFT
    if request.method != 'POST':
        return redirect('teacher_portal:dashboard')
    original = get_object_or_404(UnitOutline, pk=pk)
    assessments = list(original.assessments.all())
    original.pk = None
    original.name = f'Copy of {original.name}'
    original.status = 'DRAFT'
    original.planner_pdf = None
    original.save()
    for a in assessments:
        a.pk = None
        a.unit = original
        a.save()
    messages.success(request, f'Cloned to "{original.name}".')
    return redirect('teacher_portal:unit_edit', pk=original.pk)


def generate_pdf_file(unit):
    # Build the unit-outline PDF in memory and return the buffer
    buffer = BytesIO()
    p = canvas.Canvas(buffer)

    # Title
    p.setFont('Helvetica-Bold', 16)
    p.drawString(72, 800, f'Unit Outline: {unit.name}')

    # Unit details table
    rows = [
        ['Field', 'Value'],
        ['Code', unit.code],
        ['Year Level', unit.year_level or '-'],
        ['Semester', unit.semester or '-'],
        ['Status', unit.get_status_display()],
        ['Release as VET', 'Yes' if unit.release_as_vet else 'No'],
    ]

    # Assessment rows
    for a in unit.assessments.all():
        rows.append([f'Assessment: {a.name}',
                     f'{a.weight}% due {a.due_date or "TBA"}'])

    # Draw + finalise
    table = Table(rows)
    table.wrapOn(p, 450, 600)
    table.drawOn(p, 72, 500)
    p.showPage()
    p.save()
    buffer.seek(0)
    return buffer


def unit_print(request, pk):
    # Download the unit outline as a PDF, with the uploaded planner appended if present
    unit = get_object_or_404(UnitOutline, pk=pk)
    generated = generate_pdf_file(unit)
    merger = PdfWriter()
    merger.append(PdfReader(generated))

    # Append the uploaded planner if one is attached
    if unit.planner_pdf:
        try:
            merger.append(PdfReader(unit.planner_pdf.path))
        except Exception:
            pass

    out = BytesIO()
    merger.write(out)
    out.seek(0)
    return FileResponse(out, as_attachment=True,
                        filename=f'unit_{unit.code}.pdf')


def calendar_view(request):
    # Month grid showing every assessment start and due date
    today = date.today()
    try:
        year = int(request.GET.get('year', today.year))
        month = int(request.GET.get('month', today.month))
    except ValueError:
        year, month = today.year, today.month
    if not 1 <= month <= 12:
        month = today.month

    # Build day list of events for this month
    events = {}
    items = AssessmentItem.objects.filter(
        due_date__year=year, due_date__month=month
    ).select_related('unit')
    for item in items:
        events.setdefault(item.due_date.day, []).append({
            'label': f'{item.name} due',
            'unit': item.unit.code,
            'unit_id': item.unit.pk,
        })
    starts = AssessmentItem.objects.filter(
        start_date__year=year, start_date__month=month
    ).select_related('unit')
    for item in starts:
        events.setdefault(item.start_date.day, []).append({
            'label': f'{item.name} start',
            'unit': item.unit.code,
            'unit_id': item.unit.pk,
        })

    # Shape weeks for the template
    cal = cal_module.Calendar(firstweekday=0)
    weeks = []
    for week in cal.monthdayscalendar(year, month):
        weeks.append([{
            'number': day if day else '',
            'other_month': day == 0,
            'is_today': day and today == date(year, month, day),
            'events': events.get(day, []),
        } for day in week])

    # Prev / next month navigation
    prev_month = month - 1 or 12
    prev_year = year - 1 if month == 1 else year
    next_month = month + 1 if month < 12 else 1
    next_year = year + 1 if month == 12 else year

    return render(request, 'calendar.html', {
        'month_name': MONTH_NAMES[month],
        'year': year,
        'weeks': weeks,
        'prev_month': prev_month, 'prev_year': prev_year,
        'next_month': next_month, 'next_year': next_year,
    })
