from django.db import models


# Core unit record
class UnitOutline(models.Model):
    STATUS_CHOICES = [
        ('DRAFT', 'Draft'),
        ('PUBLISHED', 'Published'),
        ('ARCHIVED', 'Archived'),
    ]

    name = models.CharField(max_length=200)
    code = models.CharField(max_length=20)
    year_level = models.CharField(max_length=20, blank=True)
    semester = models.CharField(max_length=40, blank=True, default='Semester 1, 2026')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='DRAFT')
    planner_pdf = models.FileField(upload_to='planners/', null=True, blank=True)
    release_as_vet = models.BooleanField(default=False, verbose_name='Release as VET')
    created_date = models.DateTimeField(auto_now_add=True)
    modified_date = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-modified_date']

    def __str__(self):
        return f"{self.name} ({self.code})"


# Per unit assessment row
class AssessmentItem(models.Model):
    unit = models.ForeignKey(UnitOutline, on_delete=models.CASCADE, related_name='assessments')
    name = models.CharField(max_length=200)
    weight = models.PositiveIntegerField(default=0, help_text='Percentage weighting (0-100)')
    start_date = models.DateField(null=True, blank=True)
    due_date = models.DateField(null=True, blank=True)

    class Meta:
        ordering = ['due_date', 'id']

    def __str__(self):
        return f"{self.name} ({self.unit.code})"
