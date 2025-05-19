from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

class Quiz(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    allow_retake = models.BooleanField(default=True, verbose_name='امکان شرکت مجدد')
    
    def __str__(self):
        return self.title

class Question(models.Model):
    QUESTION_TYPES = (
        ('text', 'متنی'),
        ('image', 'تصویری'),
        ('video', 'ویدیویی'),
    )
    
    question_type = models.CharField(max_length=10, choices=QUESTION_TYPES, default='text', verbose_name='نوع سوال')
    question_text = models.TextField(verbose_name='متن سوال', null=True, blank=True,)
    question_image = models.ImageField(upload_to='questions/images/', null=True, blank=True, verbose_name='تصویر سوال')
    question_video = models.FileField(upload_to='questions/videos/', null=True, blank=True, verbose_name='ویدیو سوال')
    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE, related_name='questions')
    points = models.IntegerField(default=1, null=True, blank=True,)  # امتیاز داینامیک برای هر سوال
    order = models.IntegerField(default=0, null=True, blank=True,)
    
    def __str__(self):
        return self.question_text
    
    class Meta:
        ordering = ['order']

class Choice(models.Model):
    CHOICE_TYPES = (
        ('text', 'متنی'),
        ('image', 'تصویری'),
    )
    
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    choice_type = models.CharField(max_length=10, choices=CHOICE_TYPES, default='text', verbose_name='نوع گزینه')
    choice_text = models.CharField(max_length=200, null=True, blank=True, verbose_name='متن گزینه')
    choice_image = models.ImageField(upload_to='choices/images/', null=True, blank=True, verbose_name='تصویر گزینه')
    is_correct = models.BooleanField(default=False, verbose_name='گزینه صحیح')
    
    def __str__(self):
        return f"گزینه برای سوال {self.question.id}"

class QuizAttempt(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='quiz_attempts')
    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE, related_name='attempts')
    start_time = models.DateTimeField(default=timezone.now)
    end_time = models.DateTimeField(null=True, blank=True)
    score = models.IntegerField(default=0)
    completed = models.BooleanField(default=False)
    
    def __str__(self):
        return f"{self.user.username} - {self.quiz.title}"
    
    def calculate_duration(self):
        if self.end_time:
            return (self.end_time - self.start_time).total_seconds()
        return None
    
    def calculate_score(self):
        total = 0
        for answer in self.answers.all():
            if answer.selected_choice and answer.selected_choice.is_correct:
                total += answer.question.points
        return total
    
    def complete(self):
        self.end_time = timezone.now()
        self.score = self.calculate_score()
        self.completed = True
        self.save()

class Answer(models.Model):
    attempt = models.ForeignKey(QuizAttempt, on_delete=models.CASCADE, related_name='answers')
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    selected_choice = models.ForeignKey(Choice, on_delete=models.CASCADE, null=True, blank=True)
    
    def __str__(self):
        return f"پاسخ به سوال {self.question.id}"
