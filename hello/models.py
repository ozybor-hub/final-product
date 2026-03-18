from django.db import models
from django.conf import settings


class UnitOutline(models.Model):
    # unit outline created by a teacher.

    STATUS_CHOICES = [
        ('DRAFT', 'Draft'),
        ('PUBLISHED', 'Published'),
        ('ARCHIVED', 'Archived'),
    ]

    name = models.CharField(max_length=200)
    code = models.CharField(max_length=20)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='DRAFT')
    teacher = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='unit_outlines')
    created_date = models.DateTimeField(auto_now_add=True)
    modified_date = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-modified_date']
        verbose_name = 'Unit Outline'
        verbose_name_plural = 'Unit Outlines'

    def __str__(self):
        return f"{self.name} ({self.code})"

    def clone(self, new_owner=None):
        """Create a copy of this unit outline as a new DRAFT."""
        original_pk = self.pk
        self.pk = None
        self.status = 'DRAFT'
        self.name = f"Copy of {self.name}"
        self.created_date = None

        if new_owner:
            self.teacher = new_owner

        self.save()
        return self


class AssessmentItem(models.Model):
    # assessment item within a unit outline.

    unit_outline = models.ForeignKey(UnitOutline, on_delete=models.CASCADE, related_name='assessment_items')
    name = models.CharField(max_length=200)
    due_date = models.DateField(null=True, blank=True)
    description = models.TextField(blank=True)
    weight = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    status = models.CharField(max_length=20, default='Outline Pending')

    def __str__(self):
        return f"{self.name} - {self.unit_outline.name}"
