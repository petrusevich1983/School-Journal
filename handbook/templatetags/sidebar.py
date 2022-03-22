from django import template

from persons.models import Teacher, User


register = template.Library()


@register.inclusion_tag('persons/tpl/schoolboy_sidebar_tpl.html', name='schoolboy_sidebar')
def schoolboy_sidebar(user): # сайтбар для ученика
    group_schoolboy = User.objects.select_related('schoolboy__group').get(pk=user.id)
    user_group_manager = User.objects.select_related('teacher')\
        .get(teacher__group_manager=group_schoolboy.schoolboy.group_id)
    return {'user': user, 'user_group_manager': user_group_manager}


@register.inclusion_tag('persons/tpl/teacher_sidebar_tpl.html', name='teacher_sidebar')
def teacher_sidebar(user): # сайтбар для учителя.
    teacher = Teacher.objects.get(user=user.id)
    return {'teacher': teacher, 'user': user}