from django.core.exceptions import PermissionDenied

from journal.settings import TEACHER, SCHOOLBOY
from persons.models import Teacher


class TeacherPermissionsMixin:
    """
    Суперпользователь или учитель.
    """
    def dispatch(self, request, *args, **kwargs):
        if not self.has_permissions():
            raise PermissionDenied()
        return super().dispatch(request, *args, **kwargs)

    def has_permissions(self):
        return self.request.user.is_superuser or self.request.user.user_status == TEACHER


class TeacherLessonPermissionsMixin(TeacherPermissionsMixin):
    """
    Учитель, который является преподавателем предмета.
    """
    def has_permissions(self):
        if self.request.method == 'POST':
            lesson_id = self.request.POST.get('lesson')
        else:
            lesson_id = self.kwargs['lesson_id']
        teacher = Teacher.objects.prefetch_related('lessons').filter(user=self.request.user, lessons=lesson_id).exists()
        return teacher or self.request.user.is_superuser


class SchoolboyPermissionsMixin(TeacherPermissionsMixin):
    """
    Суперпользователь или ученик.
    """
    def has_permissions(self):
        return self.request.user.is_superuser or self.request.user.user_status == SCHOOLBOY