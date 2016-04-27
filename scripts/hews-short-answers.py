
import datetime
import json
import os

from codecs import open

def run(): 
    
    from django.contrib.auth.models import User
    from django.db.models import Sum, Max, Min, Avg
    from django.utils.html import strip_tags
    
    from oppia.models import Activity, Course, Cohort, CourseCohort, Participant, Tracker
    from oppia.quiz.models import Quiz, Question, QuizQuestion, QuizAttempt, QuizAttemptResponse, Response
    
    cohort_id = 23
    
    students = User.objects.filter(participant__cohort_id=cohort_id, participant__role=Participant.STUDENT).order_by('username')
    courses = Course.objects.filter(coursecohort__cohort__pk=cohort_id, shortname__in=['pnc-et','anc1-et','anc2-et'])
    
    quiz_acts = Activity.objects.filter(section__course__=courses, type=Activity.QUIZ).values_list('digest',flat=True)
    
    date = datetime.datetime.now().strftime('%Y-%m-%d')
    output_file = os.path.join(os.path.dirname(os.path.realpath(__file__)), '..', '_output', 'hew-short-answers-' + date + '.html')
    out_file = open(output_file, 'w', 'utf-8')
    
    out_file.write("<html>")
    out_file.write("<head>")
    out_file.write('<meta http-equiv="Content-Type" content="text/html;charset=utf-8" />')
    out_file.write("<style> td {text-align:center;} #footer { font-size:small; font-style:italic; } </style>")
    out_file.write("</head>")
    out_file.write("<body>")
    
    out_file.write("<table>")
    out_file.write("<tr>")
    out_file.write("<th>Question</th>")
    out_file.write("<th>QARID</th>")
    out_file.write("<th>Responses</th>")
    out_file.write("<th>Score</th>")
    out_file.write("<th>Revised Score</th>")
    out_file.write("</tr>")
    
    quizzes = Quiz.objects.filter(quizprops__value__in=quiz_acts, quizprops__name="digest")
    for quiz in quizzes:
        sa_questions = Question.objects.filter(type='shortanswer',quizquestion__quiz=quiz)
        for sa_question in sa_questions:
            print title_lang(sa_question.title,'en')
            out_file.write("<tr>")
            out_file.write("<td colspan='5'>%s</td>" % title_lang(sa_question.title,"en"))
            out_file.write("</tr>")
            
            sa_responses = Response.objects.filter(question=sa_question)
            
            out_file.write("<tr>")
            out_file.write("<td colspan='5'>Correct responses:")
            out_file.write("<ul>")
            for sa_response in sa_responses:
                out_file.write("<li>%s (%d)</li>" % (sa_response.title, sa_response.score))
            out_file.write("</ul>")
            out_file.write("</tr>")
    
            user_responses = QuizAttemptResponse.objects.filter(quizattempt__user__in=students, question=sa_question)
            for ur in user_responses:
                if ur.score == 0:
                    out_file.write("<tr>")
                    out_file.write("<td>&nbsp;</td>")
                    print ur.text
                    out_file.write("<td>%d</td>" % ur.id)
                    out_file.write("<td>" + ur.text + "</td>")
                    out_file.write("<td>%s</td>" % ur.score)
                    out_file.write("<td>&nbsp;</td>")
                    out_file.write("</tr>")
    
    out_file.write("</table>")   
    out_file.write("<div id='footer'>Report generated at %s by script %s</div>" % (datetime.datetime.now().strftime('%Y-%m-%d %H:%M'),os.path.realpath(__file__)))
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