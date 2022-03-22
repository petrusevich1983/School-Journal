from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import JsonResponse
from django.shortcuts import render, get_object_or_404
from django.views import View
from django.views.generic import ListView, DetailView

from handbook.models import GroupSchoolboy, Lesson, Score
from journal.permissions import TeacherPermissionsMixin, TeacherLessonPermissionsMixin
from journal.settings import TEACHER
from persons.models import User
from utils.service import ScoreJournalMixin


class GroupSchoolboyListView(LoginRequiredMixin, TeacherPermissionsMixin, ListView):
    """
    Список классов
    """
    template_name = 'journal/group_list.html'
    context_object_name = 'users_teachers'

    def get_queryset(self):
        queryset = User.objects.select_related('teacher__group_manager__grade').filter(user_status=TEACHER)
        return queryset


class GroupSchoolboyDetailView(LoginRequiredMixin, TeacherPermissionsMixin, DetailView):
    """
    Информация о классе.
    """
    model = GroupSchoolboy
    template_name = 'journal/group_detail.html'
    context_object_name = 'group'

    def get_context_data(self, **kwargs):
        context = super(GroupSchoolboyDetailView, self).get_context_data()
        context['schoolboys'] = User.objects.select_related('schoolboy__group')\
            .filter(schoolboy__group_id=self.kwargs['pk'])
        return context


class ScoreLessonListView(LoginRequiredMixin, TeacherLessonPermissionsMixin, ScoreJournalMixin, ListView):
    """
    Журнал оценок класса по предмету.
    """
    template_name = 'journal/journal_lesson_list.html'
    context_object_name = 'scores'
    permission_denied_message = 'В доступе отказано'

    def get_queryset(self):
        group_schoolboy = GroupSchoolboy.objects.select_related('grade')
        self.group = get_object_or_404(group_schoolboy, id=self.kwargs['group_id'])
        self.lesson = get_object_or_404(Lesson, id=self.kwargs['lesson_id'])
        queryset = Score.objects.select_related('group', 'lesson')\
            .filter(group_id=self.kwargs['group_id'], lesson_id=self.kwargs['lesson_id'])
        return queryset

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super(ScoreLessonListView, self).get_context_data(**kwargs)
        date_period = self.create_date_period_list()
        schoolboys = User.objects.select_related('schoolboy', 'schoolboy__group').filter(schoolboy__group=self.group)
        scores = Score.objects.select_related('group', 'lesson')\
            .filter(created__in=date_period, lesson_id=self.lesson, group_id=self.group)

        context['date_period'] = date_period
        context['schoolboys'] = schoolboys
        context['scores_dict'] = self.create_scores_dict(date_period,
                                                         scores.values('id', 'schoolboy', 'score', 'created'),
                                                         schoolboys, 'schoolboy')
        context['group'] = self.group
        context['lesson'] = self.lesson
        return context


class AddScore(LoginRequiredMixin, TeacherLessonPermissionsMixin, TeacherPermissionsMixin, View):
    """
    Добавление оценки.
    """
    def post(self, request):
        score_id = request.POST.get('score_id')
        if score_id == '0':
            score_id = None
        score_params = {
            'score': request.POST.get('score_value'),
            'group_id': request.POST.get('group'),
            'lesson_id': request.POST.get('lesson'),
            'schoolboy_id': request.POST.get('schoolboy'),
            'teacher_id': request.POST.get('teacher'),
            'score_status_id': request.POST.get('score_status'),
            'created': request.POST.get('score_date'),
        }

        if score_params['score']:
            Score.objects.update_or_create(id=score_id, defaults=score_params)
            return JsonResponse({'status': 'ok'})
        else:
            Score.objects.get(id=score_id).delete()
            return JsonResponse({'status': 'ok'})
