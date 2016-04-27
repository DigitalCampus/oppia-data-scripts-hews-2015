'''
Takes the best score for each quiz attempt during a particular time period and generates the average

'''

import datetime
import json
import os

from codecs import open

def run(): 
    
    from django.contrib.auth.models import User
    from django.db.models import Sum, Max, Min, Avg
    from django.utils.html import strip_tags
    
    from oppia.models import Activity, Course, Cohort, CourseCohort, Participant, Tracker
    from oppia.quiz.models import Quiz, QuizQuestion, QuizAttempt, QuizAttemptResponse
    
    COHORT_ID = 23
    START_DATE = datetime.datetime(2015,5,01,0,0,0)
    print START_DATE
    END_DATE = datetime.datetime(2015,07,31,23,59,59)
    print END_DATE
    
    students = User.objects.filter(participant__cohort_id=COHORT_ID, participant__role=Participant.STUDENT).order_by('username')
    all_courses = Course.objects.filter(coursecohort__cohort_id = COHORT_ID, shortname__in=['anc1-et','anc2-et','pnc-et']).order_by('title')
    all_quizzes = Activity.objects.filter(section__course__in=all_courses, baseline=False, type=Activity.QUIZ)
    quiz_digests = all_quizzes.values_list('digest', flat=True).distinct()
    quizzes = Quiz.objects.filter(quizprops__name='digest', quizprops__value__in=quiz_digests)
    
    output_file = os.path.join(os.path.dirname(os.path.realpath(__file__)), '..', '_output', 'hew-quiz-avg-scores.html')
    out_file = open(output_file, 'w', 'utf-8')
    
    out_file.write("<html>")
    out_file.write("<head>")
    out_file.write('<meta http-equiv="Content-Type" content="text/html;charset=utf-8" />')
    out_file.write("<style> td {text-align:center;}</style>")
    out_file.write("</head>")
    out_file.write("<body>")
    
    out_file.write("<h2>Average Scores for %s to %s</h2>" % (START_DATE, END_DATE))
    
    out_file.write("<table>")
    
    out_file.write("<tr>")
    out_file.write("<th>Student</th>")
    out_file.write("<th>No quizzes</th>")
    out_file.write("<th>No quizzes attempted</th>")
    out_file.write("<th>Avg Score</th>")
    out_file.write("</tr>")
    
    for s in students:
        print s.first_name + " " + s.last_name
        out_file.write("<tr>")
        out_file.write("<td>%s %s</td>" % (s.first_name, s.last_name))
        out_file.write("<td>%d</td>" % (all_quizzes.count()))
        
        no_attempted = 0
        running_score = 0
        
        for q in quizzes:
            qas = QuizAttempt.objects.filter(quiz=q,user=s,submitted_date__gte=START_DATE, submitted_date__lte=END_DATE).aggregate(user_max_score=Max('score'), max_score=Max('maxscore'))
            if qas['user_max_score']:
                no_attempted+=1
                running_score += qas['user_max_score']*100/qas['max_score']
        
        avg_score = running_score/all_quizzes.count()
        out_file.write("<td>%d</td>" % (no_attempted))
        out_file.write("<td>%d</td>" % (avg_score))
        out_file.write("</tr>")
          
    out_file.write("</table>")   
    out_file.write("</body></html>")
    out_file.close()
   
def title_lang(title,lang):
    try:
        titles = json.loads(title)
        if lang in titles:
            return titles[lang]
        else:
            for l in titles:
                return titles[l]
    except:
        pass
    return title   
    
if __name__ == "__main__":
    import django
    django.setup()
    run() 