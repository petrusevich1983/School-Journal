from django.urls import path

from persons.views import TeacherListView, TeacherDetailView, SchoolboyCreateView, SchoolboyUpdateView, \
    SchoolboyDetailView, SchoolboyLkDetailView, TeacherCreateView

urlpatterns = [
    path('teacher/', TeacherListView.as_view(), name='teacher_list'),
    path('teacher/info/<int:pk>/', TeacherDetailView.as_view(), name='teacher_detail'),
    path('teacher/add/', TeacherCreateView.as_view(), name='teacher_add'),
    path('schoolboy/add/', SchoolboyCreateView.as_view(), name='schoolboy_add'),
    path('schoolboy/update/<int:pk>/', SchoolboyUpdateView.as_view(), name='schoolboy_update'),
    path('schoolboy/info/<int:pk>/', SchoolboyDetailView.as_view(), name='schoolboy_detail'),
    path('schoolboy/', SchoolboyLkDetailView.as_view(), name='schoolboy_lk'),
    ]