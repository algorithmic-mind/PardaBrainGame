from django.contrib import admin
from .models import Quiz, Question, Choice, QuizAttempt, Answer

class ChoiceInline(admin.TabularInline):
    model = Choice
    extra = 4

class QuestionAdmin(admin.ModelAdmin):
    inlines = [ChoiceInline]
    list_display = ('question_text', 'quiz', 'points', 'order')
    list_filter = ('quiz',)
    search_fields = ('question_text',)

class QuestionInline(admin.TabularInline):
    model = Question
    extra = 1
    show_change_link = True

class QuizAdmin(admin.ModelAdmin):
    inlines = [QuestionInline]
    list_display = ('title', 'created_at', 'question_count', 'allow_retake')
    search_fields = ('title', 'description')
    list_filter = ('created_at', 'allow_retake')
    
    def question_count(self, obj):
        return obj.questions.count()
    question_count.short_description = 'تعداد سوالات'

class AnswerInline(admin.TabularInline):
    model = Answer
    extra = 0

class QuizAttemptAdmin(admin.ModelAdmin):
    inlines = [AnswerInline]
    list_display = ('user', 'quiz', 'start_time', 'end_time', 'score', 'completed')
    list_filter = ('quiz', 'completed')
    search_fields = ('user__username', 'quiz__title')

admin.site.register(Quiz, QuizAdmin)
admin.site.register(Question, QuestionAdmin)
admin.site.register(Choice)
admin.site.register(QuizAttempt, QuizAttemptAdmin)
admin.site.register(Answer)