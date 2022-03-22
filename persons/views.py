from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.messages.views import SuccessMessageMixin
from django.db.models import Count, Sum, Avg
from django.contrib import messages
from django.urls import reverse_lazy
from django.views.generic import ListView, DetailView, CreateView, UpdateView

from handbook.models import Lesson, Score
from journal.permissions import TeacherPermissionsMixin, SchoolboyPermissionsMixin, TeacherLessonPermissionsMixin
from journal.settings import TEACHER, SCHOOLBOY
from persons.forms import UserCreateForm, SchoolboyForm, ContactForm, UserUpdateForm, SchoolboyFormSet, ContactFormSet, \
    TeacherForm
from persons.models import Teacher, Schoolboy, Contact, User
from utils.service import ScoreJournalMixin


class TeacherListView(LoginRequiredMixin, ListView):
    """
    Список учителей
    """
    template_name = 'persons/teacher_list.html'

    def get_queryset(self):
        queryset = User.objects.select_related('teacher__group_manager__grade').filter(user_status=TEACHER)
        return queryset

class TeacherDetailView(LoginRequiredMixin, DetailView):
    """
    Информация об учителе
    """
    model = Teacher
    template_name = 'persons/teacher_detail.html'

    def get_queryset(self):
        queryset = User.objects.select_related('teacher__group_manager__grade').filter(user_status=TEACHER)
        return queryset


class SchoolboyDetailView(LoginRequiredMixin, TeacherPermissionsMixin, DetailView):
    """
    Информация об ученике
    """
    template_name = 'persons/schoolboy_detail.html'

    def get_queryset(self):
        queryset = User.objects.select_related('schoolboy__group__grade', 'contact').filter(user_status=SCHOOLBOY)
        return queryset


class SchoolboyLkDetailView(LoginRequiredMixin, SchoolboyPermissionsMixin, ScoreJournalMixin, DetailView):
    """
    Личный кабинет ученика.
    """
    template_name = 'persons/schoolboy_lk.html'
    context_object_name = 'schoolboy'

    def get_object(self, queryset=None):
        return User.objects.select_related('schoolboy', 'contact').get(pk=self.request.user.pk)

    def get_context_data(self, **kwargs):
        context = super(SchoolboyLkDetailView, self).get_context_data(**kwargs)
        date_period = self.create_date_period_list()
        lessons = Lesson.objects.filter(grade__group__schoolboys=self.request.user.schoolboy.id)
        scores = Score.objects.filter(schoolboy_id=self.request.user.pk,
                                      created__in=date_period).values('id', 'lesson_id', 'score', 'created')

        count_scores = scores.values('score').annotate(count_score=Count('score')).order_by('-score')
        total_scores = count_scores.aggregate(sum_count=Sum('count_score'),
                                              sum_score=Avg('score'),
                                              sum_score_percent=Avg('score')*10)

        schoolboy_rating = {10: 0, 9: 0, 8: 0, 7: 0, 6: 0, 5: 0, 4: 0, 3: 0, 2: 0, 1: 0}
        for item in count_scores:
            schoolboy_rating[item['score']] = item['count_score']

        context['rating'] = schoolboy_rating
        context['total_scores'] = total_scores
        context['date_period'] = date_period
        context['lessons'] = lessons
        context['scores_dict'] = self.create_scores_dict(date_period, scores, lessons, 'lesson_id')
        return context


class SchoolboyCreateView(LoginRequiredMixin, TeacherPermissionsMixin, SuccessMessageMixin, CreateView):
    """
    Создание нового ученика.
    """
    form_class = UserCreateForm
    template_name = 'persons/schoolboy_create.html'
    success_url = reverse_lazy('schoolboy_add')
    success_message = 'Ученик успешно добавлен.'

    def get_context_data(self, **kwargs):
        data = super(SchoolboyCreateView, self).get_context_data(**kwargs)
        data['schoolboy_form'] = SchoolboyForm()
        data['contact_form'] = ContactForm()
        return data

    def post(self, request, *args, **kwargs):
        form = self.get_form()
        schoolboy_form = SchoolboyForm(self.request.POST)
        contact_form = ContactForm(self.request.POST)
        if form.is_valid() and schoolboy_form.is_valid() and contact_form.is_valid():
            user = form.save(commit=False)
            user.user_status = SCHOOLBOY
            schoolboy = schoolboy_form.save(commit=False)
            contact = contact_form.save(commit=False)
            schoolboy.user = user
            contact.user = user
            user.save()
            schoolboy.save()
            contact.save()
            return self.form_valid(form)
        else:
            messages.error(request, 'Ошибка сохранения !')
            return self.render_to_response({'form': form, 'schoolboy_form': schoolboy_form, 'contact_form': contact_form})


class SchoolboyUpdateView(LoginRequiredMixin, TeacherPermissionsMixin, SuccessMessageMixin, UpdateView):
    """
    Редактирование ученика.
    """
    model = User
    queryset = User.objects.filter(user_status=SCHOOLBOY)
    form_class = UserUpdateForm
    template_name = 'persons/schoolboy_update.html'
    success_message = 'Данные ученика успешно обновлены.'

    def post(self, request, *args, **kwargs):
        form = UserUpdateForm(self.request.POST)
        schoolboy_formset = SchoolboyFormSet(self.request.POST, prefix='schoolboy')
        contact_formset = ContactFormSet(self.request.POST, prefix='contact')
        if schoolboy_formset.is_valid() and contact_formset.is_valid():
            contact_formset.save()
            schoolboy_formset.save()
            return super(SchoolboyUpdateView, self).post(self.request.POST)
        else:
            messages.error(request, 'Ошибка сохранения !')
            return self.render_to_response(
                {'form': form, 'schoolboy_form': schoolboy_formset, 'contact_form': contact_formset}
            )

    def get_context_data(self, **kwargs):
        data = super(SchoolboyUpdateView, self).get_context_data(**kwargs)
        schoolboy_formset = SchoolboyFormSet(queryset=Schoolboy.objects.filter(user_id=self.kwargs['pk']),
                                             prefix='schoolboy')
        contact_formset = ContactFormSet(queryset=Contact.objects.filter(user_id=self.kwargs['pk']), prefix='contact')

        data['schoolboy_form'] = schoolboy_formset
        data['contact_form'] = contact_formset
        return data

    def get_success_url(self):
        return reverse_lazy('schoolboy_update', kwargs={'pk': self.kwargs['pk']})


class TeacherCreateView(LoginRequiredMixin, TeacherPermissionsMixin, SuccessMessageMixin, CreateView):
    """
    Создание нового учителя.
    """
    form_class = UserCreateForm
    template_name = 'persons/teacher_create.html'
    success_url = reverse_lazy('teacher_add')
    success_message = 'Учитель успешно добавлен.'

    def get_context_data(self, **kwargs):
        data = super(TeacherCreateView, self).get_context_data(**kwargs)
        data['teacher_form'] = TeacherForm()
        data['contact_form'] = ContactForm()
        return data

    def post(self, request, *args, **kwargs):
        form = self.get_form()
        teacher_form = TeacherForm(self.request.POST)
        contact_form = ContactForm(self.request.POST)
        if form.is_valid() and teacher_form.is_valid() and contact_form.is_valid():
            user = form.save(commit=False)
            user.user_status = TEACHER
            teacher = teacher_form.save(commit=False)
            contact = contact_form.save(commit=False)
            teacher.user = user
            contact.user = user
            user.save()
            teacher.save()
            contact.save()
            return self.form_valid(form)
        else:
            messages.error(request, 'Ошибка сохранения !')
            return self.render_to_response({'form': form, 'teacher_form': teacher_form, 'contact_form': contact_form})