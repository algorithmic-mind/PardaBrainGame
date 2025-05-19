from django.urls import path
from . import views

app_name = 'quiz'

urlpatterns = [
    path('', views.home, name='home'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('quizzes/', views.quiz_list, name='quiz_list'),
    path('quiz/<int:quiz_id>/', views.quiz_detail, name='quiz_detail'),
    path('quiz/<int:quiz_id>/start/', views.start_quiz, name='start_quiz'),
    path('attempt/<int:attempt_id>/', views.quiz_attempt, name='quiz_attempt'),
    path('attempt/<int:attempt_id>/question/<int:question_id>/', views.answer_question, name='answer_question'),
    path('attempt/<int:attempt_id>/complete/', views.complete_quiz, name='complete_quiz'),
    path('attempt/<int:attempt_id>/results/', views.quiz_results, name='quiz_results'),
]