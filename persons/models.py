from django.conf import settings
from django.contrib.auth.models import AbstractUser, UserManager
from django.db import models
from django.urls import reverse_lazy

from journal.settings import TEACHER, SCHOOLBOY


class User(AbstractUser):
    """
    Пользователь
    """
    GENDER_CHOICES = [('М', 'М'), ('Ж', 'Ж')]
    USER_STATUS_CHOICES = [(TEACHER, 'Учитель'), (SCHOOLBOY, 'Ученик')]
    middle_name = models.CharField('Отчество', max_length=130, blank=True)
    sex = models.CharField('Пол', choices=GENDER_CHOICES, max_length=1)
    birth_date = models.DateField('Дата рождения', blank=True, null=True)
    photo = models.ImageField(upload_to='persons/', default='static/img/default-user.png', blank=True)
    description = models.TextField('Характеристика', blank=True)
    user_status = models.CharField('Статус пользователя', choices=USER_STATUS_CHOICES, max_length=15)
    updated = models.DateField('Дата обновления', auto_now=True)

    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = ['email']

    objects = UserManager()

    def __str__(self):
        return self.username

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'


class Teacher(models.Model):
    """
    Учителя
    """
    position = models.CharField('Должность', max_length=99)
    group_manager = models.ForeignKey('handbook.GroupSchoolboy', related_name='teacher',
                                      verbose_name='Руководит классом',
                                      on_delete=models.SET_NULL, null=True, blank=True)
    lessons = models.ManyToManyField('handbook.Lesson', related_name='teachers', verbose_name='Ведет предметы')
    user = models.OneToOneField(settings.AUTH_USER_MODEL, related_name='teacher', on_delete=models.CASCADE)

    def get_absolute_url(self):
        return reverse_lazy('teacher_detail', kwargs={'pk': self.user_id})

    class Meta:
        verbose_name = 'Учитель'
        verbose_name_plural = 'Учителя'


class Schoolboy(models.Model):
    """
    Ученики
    """
    group = models.ForeignKey('handbook.GroupSchoolboy', related_name='schoolboys', verbose_name='Состоит в классе',
                              on_delete=models.CASCADE)
    user = models.OneToOneField(settings.AUTH_USER_MODEL, related_name='schoolboy', on_delete=models.CASCADE)

    def get_absolute_url(self):
        return reverse_lazy('schoolboy_detail', kwargs={'pk': self.user_id})

    class Meta:
        verbose_name = 'Ученик'
        verbose_name_plural = 'Ученики'


class Contact(models.Model):
    """
    Контакты учеников, родителей, учителей
    """
    phone1 = models.CharField(max_length=12, blank=True, verbose_name='Телефон 1')
    phone2 = models.CharField(max_length=12, blank=True, verbose_name='Телефон 2')
    phone3 = models.CharField(max_length=12, blank=True, verbose_name='Телефон 3')
    user = models.OneToOneField(settings.AUTH_USER_MODEL, related_name='contact', null=True, blank=True,
                                verbose_name='Контактные данные', on_delete=models.CASCADE)

    def __str__(self):
        return self.phone1

    class Meta:
        verbose_name = 'Контакт'
        verbose_name_plural = 'Контакты'
