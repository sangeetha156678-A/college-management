from django.contrib import admin

from academics.models import Department, Semester, Subject, Year


class YearInline(admin.TabularInline):
  model = Year
  extra = 0


class SemesterInline(admin.TabularInline):
  model = Semester
  extra = 0


class SubjectInline(admin.TabularInline):
  model = Subject
  extra = 0
  fields = ('code', 'name', 'credits')


@admin.register(Department)
class DepartmentAdmin(admin.ModelAdmin):
  list_display = ('code', 'name', 'duration_years', 'is_active')
  list_filter = ('is_active',)
  search_fields = ('code', 'name')
  inlines = [YearInline]


@admin.register(Year)
class YearAdmin(admin.ModelAdmin):
  list_display = ('department', 'number')
  list_filter = ('department',)
  inlines = [SemesterInline]


@admin.register(Semester)
class SemesterAdmin(admin.ModelAdmin):
  list_display = ('year', 'number')
  list_filter = ('year__department', 'year')
  inlines = [SubjectInline]


@admin.register(Subject)
class SubjectAdmin(admin.ModelAdmin):
  list_display = ('code', 'name', 'department', 'semester', 'credits')
  list_filter = ('department', 'semester__year')
  search_fields = ('code', 'name')
