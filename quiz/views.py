from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from .models import Quiz, Question, Choice, QuizAttempt, Answer

def home(request):
    """صفحه اصلی سایت"""
    latest_quizzes = Quiz.objects.order_by('-created_at')[:5]
    context = {
        'title': 'صفحه اصلی',
        'latest_quizzes': latest_quizzes
    }
    return render(request, 'quiz/index.html', context)

@login_required
def dashboard(request):
    """داشبورد کاربر"""
    user_attempts = QuizAttempt.objects.filter(user=request.user).order_by('-start_time')
    completed_attempts = user_attempts.filter(completed=True)
    
    # محاسبه آمار کاربر
    total_quizzes_taken = completed_attempts.count()
    total_score = sum(attempt.score for attempt in completed_attempts)
    
    context = {
        'title': 'داشبورد',
        'user_attempts': user_attempts,
        'total_quizzes_taken': total_quizzes_taken,
        'total_score': total_score
    }
    return render(request, 'quiz/dashboard.html', context)

@login_required
def quiz_list(request):
    """لیست تمام آزمون‌ها"""
    quizzes = Quiz.objects.all().order_by('-created_at')
    context = {
        'title': 'لیست آزمون‌ها',
        'quizzes': quizzes
    }
    return render(request, 'quiz/quiz_list2.html', context)

from django.db.models import F, ExpressionWrapper, FloatField
from django.utils import timezone

@login_required
def quiz_detail(request, quiz_id):
    """نمایش جزئیات یک آزمون"""
    quiz = get_object_or_404(Quiz, id=quiz_id)
    
    # دریافت تلاش‌های قبلی کاربر
    user_attempts = QuizAttempt.objects.filter(
        user=request.user,
        quiz=quiz,
        completed=True
    ).order_by('-end_time')
    
    # بررسی آیا کاربر قبلاً آزمون را کامل کرده است
    user_completed = user_attempts.exists()
    
    # آیا کاربر می‌تواند مجدداً در آزمون شرکت کند
    can_retake = quiz.allow_retake or not user_completed
    
    # دریافت ۱۰ نفر برتر
    top_attempts = QuizAttempt.objects.filter(
        quiz=quiz,
        completed=True
    ).order_by('-score', 'end_time')[:10]
    
    # محاسبه درصد و زمان فرمت‌شده برای هر تلاش
    for attempt in top_attempts:
        # محاسبه درصد
        total_points = sum(q.points for q in quiz.questions.all())
        attempt.percentage = (attempt.score / total_points * 100) if total_points > 0 else 0
        
        # محاسبه زمان فرمت‌شده
        duration = attempt.calculate_duration() or 0
        if duration < 60:
            attempt.duration_formatted = f"{int(duration)} ثانیه"
        else:
            minutes = int(duration) // 60
            seconds = int(duration) % 60
            attempt.duration_formatted = f"{minutes} دقیقه و {seconds} ثانیه"
    
    context = {
        'title': quiz.title,
        'quiz': quiz,
        'user_attempts': user_attempts,
        'user_completed': user_completed,
        'can_retake': can_retake,
        'top_attempts': top_attempts
    }
    return render(request, 'quiz/quiz_detail.html', context)

@login_required
def start_quiz(request, quiz_id):
    """شروع یک آزمون جدید"""
    quiz = get_object_or_404(Quiz, id=quiz_id)
    
    # بررسی آیا کاربر قبلاً آزمون را کامل کرده است
    completed_attempts = QuizAttempt.objects.filter(
        user=request.user, 
        quiz=quiz, 
        completed=True
    ).exists()
    
    # بررسی آیا کاربر قبلاً آزمون ناتمام دارد
    existing_attempt = QuizAttempt.objects.filter(
        user=request.user, 
        quiz=quiz, 
        completed=False
    ).first()
    
    # اگر کاربر قبلاً آزمون را کامل کرده و آزمون اجازه شرکت مجدد ندارد
    if completed_attempts and not quiz.allow_retake:
        messages.warning(request, 'شما قبلاً در این آزمون شرکت کرده‌اید و امکان شرکت مجدد وجود ندارد.')
        return redirect('quiz:quiz_detail', quiz_id=quiz.id)
    
    if existing_attempt:
        # ادامه آزمون ناتمام
        return redirect('quiz:quiz_attempt', attempt_id=existing_attempt.id)
    
    # ایجاد یک تلاش جدید
    attempt = QuizAttempt.objects.create(
        user=request.user,
        quiz=quiz
    )
    
    # ایجاد پاسخ‌های خالی برای هر سوال
    for question in quiz.questions.all():
        Answer.objects.create(
            attempt=attempt,
            question=question
        )
    
    return redirect('quiz:quiz_attempt', attempt_id=attempt.id)

@login_required
def quiz_attempt(request, attempt_id):
    """صفحه اصلی تلاش آزمون"""
    attempt = get_object_or_404(QuizAttempt, id=attempt_id, user=request.user)
    
    if attempt.completed:
        return redirect('quiz:quiz_results', attempt_id=attempt.id)
    
    # پیدا کردن اولین سوال بدون پاسخ
    unanswered = attempt.answers.filter(selected_choice__isnull=True).first()
    
    if unanswered:
        return redirect('quiz:answer_question', attempt_id=attempt.id, question_id=unanswered.question.id)
    else:
        # اگر همه سوالات پاسخ داده شده‌اند
        return redirect('quiz:complete_quiz', attempt_id=attempt.id)

@login_required
def answer_question(request, attempt_id, question_id):
    """پاسخ به یک سوال"""
    attempt = get_object_or_404(QuizAttempt, id=attempt_id, user=request.user)
    question = get_object_or_404(Question, id=question_id, quiz=attempt.quiz)
    
    if attempt.completed:
        return redirect('quiz:quiz_results', attempt_id=attempt.id)
    
    # پیدا کردن یا ایجاد پاسخ برای این سوال
    answer, created = Answer.objects.get_or_create(
        attempt=attempt,
        question=question
    )
    
    if request.method == 'POST':
        choice_id = request.POST.get('choice')
        if choice_id:
            try:
                choice = get_object_or_404(Choice, id=choice_id, question=question)
                answer.selected_choice = choice
                answer.save()
                
                # پیدا کردن سوال بعدی
                next_unanswered = attempt.answers.filter(selected_choice__isnull=True).first()
                
                if next_unanswered:
                    # اگر سوال بعدی وجود دارد، به آن هدایت کن
                    return redirect('quiz:answer_question', attempt_id=attempt.id, question_id=next_unanswered.question.id)
                else:
                    # اگر همه سوالات پاسخ داده شده‌اند، آزمون را به پایان برسان
                    return redirect('quiz:complete_quiz', attempt_id=attempt.id)
            except Exception as e:
                # ثبت خطا برای اشکال‌زدایی
                print(f"خطا در ثبت پاسخ: {e}")
    
    # محاسبه شماره فعلی سوال
    questions = list(attempt.quiz.questions.all())
    try:
        current_number = questions.index(question) + 1
    except ValueError:
        current_number = 1
    total_questions = len(questions)
    
    context = {
        'title': 'آزمون',
        'attempt': attempt,
        'question': question,
        'answer': answer,
        'current_number': current_number,
        'total_questions': total_questions
    }
    return render(request, 'quiz/answer_question.html', context)

@login_required
def complete_quiz(request, attempt_id):
    """تکمیل آزمون"""
    attempt = get_object_or_404(QuizAttempt, id=attempt_id, user=request.user)
    
    if not attempt.completed:
        attempt.complete()
        messages.success(request, 'آزمون با موفقیت به پایان رسید!')
    
    return redirect('quiz:quiz_results', attempt_id=attempt.id)

@login_required
def quiz_results(request, attempt_id):
    """نمایش نتایج آزمون"""
    attempt = get_object_or_404(QuizAttempt, id=attempt_id, user=request.user)
    
    if not attempt.completed:
        return redirect('quiz:quiz_attempt', attempt_id=attempt.id)
    
    # محاسبه درصد پاسخ‌های صحیح
    total_questions = attempt.quiz.questions.count()
    correct_answers = sum(1 for answer in attempt.answers.all() 
                         if answer.selected_choice and answer.selected_choice.is_correct)
    
    percentage = (correct_answers / total_questions) * 100 if total_questions > 0 else 0
    
    context = {
        'title': 'نتایج آزمون',
        'attempt': attempt,
        'total_questions': total_questions,
        'correct_answers': correct_answers,
        'percentage': percentage,
        'duration': attempt.calculate_duration()
    }
    return render(request, 'quiz/quiz_results.html', context)
