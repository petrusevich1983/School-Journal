from django.contrib import admin

from handbook.models import Lesson, Grade, RatingItemStatus, GroupSchoolboy, Score


@admin.register(Lesson)
class LessonAdmin(admin.ModelAdmin):
    """
    Уроки.
    """
    list_display = ('name',)


@admin.register(Grade)
class GradeAdmin(admin.ModelAdmin):
    """
    Классы.
    """
    list_display = ('number', 'symbol')


@admin.register(RatingItemStatus)
class RatingItemStatusAdmin(admin.ModelAdmin):
    """
    Статусы оценок.
    """
    list_display = ('name',)


@admin.register(GroupSchoolboy)
class GroupSchoolboyAdmin(admin.ModelAdmin):
    """
    Класс
    """
    pass


@admin.register(Score)
class ScoreAdmin(admin.ModelAdmin):
    """
    Оценки.
    """
    list_display = ('schoolboy', 'lesson', 'score', 'created', 'updated', 'group')
    list_filter = ('created', 'score', 'lesson', 'group')
    search_fields = ('schoolboy__first_name', 'schoolboy__last_name')
    save_on_top = True
