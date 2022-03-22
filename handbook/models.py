from django.conf import settings
from django.db import models
from django.urls import reverse_lazy

from journal.settings import TEACHER, SCHOOLBOY


class Lesson(models.Model):
    """
    Предмет в школьной программе
    """
    name = models.CharField('Название', max_length=100)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'предмет'
        verbose_name_plural = 'Список предметов'


class Grade(models.Model):
    """
    Список существующих классов в школе
    """
    number = models.SmallIntegerField('Цифра')
    symbol = models.CharField('Символ', max_length=1)
    lessons = models.ManyToManyField(Lesson, related_name='grade', verbose_name='Уроки класса')

    def __str__(self):
        return f'{self.number}{self.symbol}'

    class Meta:
        verbose_name = 'класс'
        verbose_name_plural = 'Список классов'


class RatingItemStatus(models.Model):
    """
    Справочник статусов оценок: обычная, годовая, четверть, отменено.
    """
    name = models.CharField('Статус оценки', max_length=15)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'статус оценки'
        verbose_name_plural = 'Справочник статусов оценок'


class GroupSchoolboy(models.Model):
    """
    Классы.
    """
    grade = models.OneToOneField(Grade, related_name='group', on_delete=models.CASCADE,
                                 verbose_name='Наименование класса')
    create_group = models.DateField('Дата создания класса')
    updated = models.DateField('Дата обновления', auto_now=True)
    created = models.DateField('Дата создания', auto_now_add=True)

    def __str__(self):
        return self.grade.__str__()

    def get_absolute_url(self):
        return reverse_lazy('group_schoolboy_detail', kwargs={'pk': self.pk})

    class Meta:
        verbose_name = 'Класс'
        verbose_name_plural = 'Классы'


class Score(models.Model):
    """
    Журнал оценок
    """
    SCORE_CHOICES = [(10, '10'), (9, '9'), (8, '8'), (7, '7'), (6, '6'), (5, '5'), (4, '4'), (3, '3'), (2, '2'),
                     (1, '1')]
    group = models.ForeignKey(GroupSchoolboy, on_delete=models.CASCADE, verbose_name='Наименование класса')
    lesson = models.ForeignKey(Lesson, on_delete=models.CASCADE, verbose_name='Предмет')
    schoolboy = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='score_schoolboy', on_delete=models.CASCADE,
                                  limit_choices_to={'user_status': SCHOOLBOY}, verbose_name='Ученик')
    teacher = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='score_teacher', on_delete=models.SET_NULL,
                                null=True, limit_choices_to={'user_status': TEACHER}, verbose_name='Учитель')
    score = models.SmallIntegerField(choices=SCORE_CHOICES, verbose_name='Оценка')
    score_status = models.ForeignKey(RatingItemStatus, on_delete=models.CASCADE, verbose_name='Статус оценки')
    created = models.DateField(verbose_name='Дата создания')
    updated = models.DateTimeField(auto_now=True, verbose_name='Дата обновления')

    def __str__(self):
        return str(self.score)

    def get_absolute_url(self):
        return reverse_lazy('score_detail', kwargs={'pk': self.pk})

    class Meta:
        verbose_name = 'запись журнала'
        verbose_name_plural = 'Оценки'
        unique_together = ['schoolboy', 'lesson', 'created']
