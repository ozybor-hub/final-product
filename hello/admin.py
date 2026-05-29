from django.contrib import admin
from .models import UnitOutline, AssessmentItem


class AssessmentInline(admin.TabularInline):
    model = AssessmentItem
    extra = 1


@admin.register(UnitOutline)
class UnitOutlineAdmin(admin.ModelAdmin):
    list_display = ('name', 'code', 'year_level', 'status', 'modified_date')
    list_filter = ('status', 'year_level')
    search_fields = ('name', 'code')
    inlines = [AssessmentInline]


@admin.register(AssessmentItem)
class AssessmentItemAdmin(admin.ModelAdmin):
    list_display = ('name', 'unit', 'weight', 'start_date', 'due_date')
