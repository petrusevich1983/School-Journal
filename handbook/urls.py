from django.urls import path, include

from handbook.views import GroupSchoolboyListView, GroupSchoolboyDetailView, ScoreLessonListView, AddScore

urlpatterns = [
    path('persons/', include('persons.urls')),
    path('groups/', GroupSchoolboyListView.as_view(), name='group_schoolboy_list'),
    path('group/<int:pk>/', GroupSchoolboyDetailView.as_view(), name='group_schoolboy_detail'),
    path('<int:group_id>/<int:lesson_id>/', ScoreLessonListView.as_view(), name='score_lesson'),
    path('addscore/', AddScore.as_view(), name='add_score'),
]