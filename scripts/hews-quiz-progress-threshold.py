
import argparse
import json
import datetime
import os
import sys

from codecs import open

def run(cohort_id, threshold, period, course_range): 
    
    from django.contrib.auth.models import User
    from django.db.models import Sum, Max, Min, Avg
    from django.utils.html import strip_tags
    
    from oppia.models import Activity, Course, Cohort, CourseCohort, Participant, Tracker
    from oppia.quiz.models import Quiz, QuizQuestion, QuizAttempt, QuizAttemptResponse
    
    print "Cohort:"  + str(cohort_id)
    print "Threshold: " + str (threshold)
    print "Period: " + period
    print "Course Range: " + course_range
    
    if period == 'project': 
        START_DATE = datetime.datetime(2015,4,01,0,0,0)
        END_DATE = datetime.datetime(2016,10,31,23,59,59)
    elif period == 'training':
        START_DATE = datetime.datetime(2015,4,01,0,0,0)
        END_DATE = datetime.datetime(2015,7,31,23,59,59)
    elif period == 'cpd':
        START_DATE = datetime.datetime(2015,8,01,0,0,0)
        END_DATE = datetime.datetime(2016,10,31,23,59,59)
    elif period == 'op3.4-mar16':
        START_DATE = datetime.datetime(2015,8,01,0,0,0)
        END_DATE = datetime.datetime(2016,03,31,23,59,59)
    else:
        print "Invalid period supplied"
        sys.exit() 
    
    
    students = User.objects.filter(participant__cohort_id=cohort_id, participant__role=Participant.STUDENT).order_by('username')
    if course_range == 'ancpnc': 
        courses = Course.objects.filter(coursecohort__cohort_id = cohort_id, shortname__in=['anc1-et','anc2-et','pnc-et'])
    elif course_range == 'anc': 
        courses = Course.objects.filter(coursecohort__cohort_id = cohort_id, shortname__in=['anc1-et','anc2-et'])
    elif course_range == 'pnc': 
        courses = Course.objects.filter(coursecohort__cohort_id = cohort_id, shortname__in=['pnc-et'])
    elif course_range =='all': 
        courses = Course.objects.filter(coursecohort__cohort_id = cohort_id)
    else:
        print "Invalid course range supplied"
        sys.exit()
    
    filename = 'hew-quiz-progress-' + period + '-' + course_range + '-' + str(threshold) + '.html'
    output_file = os.path.join(os.path.dirname(os.path.realpath(__file__)), '..', '_output', filename)
    out_file = open(output_file, 'w', 'utf-8')
    
    out_file.write("<html>")
    out_file.write("<head>")
    out_file.write('<meta http-equiv="Content-Type" content="text/html;charset=utf-8" />')
    out_file.write("<style> td {text-align:center;} #footer { font-size:small; font-style:italic; } </style>")
    out_file.write("</head>")
    out_file.write("<body>")
    
    out_file.write("<h3>Courses: %s</h3>" % ','.join(courses.values_list('shortname', flat=True)))
    out_file.write("<h3>Quiz pass threshold set at: %d%%</h3>" % threshold)
    out_file.write("<h3>Date range: %s to %s</h3>" % (START_DATE.strftime('%d-%b-%Y'), END_DATE.strftime('%d-%b-%Y')))
    out_file.write("<table>")
    out_file.write("<tr>")
    out_file.write("<th>Student</th>")
    out_file.write("<th>No Quizzes</th>")
    out_file.write("<th>No Attempted</th>")
    out_file.write("<th>No Passed</th>")
    out_file.write("</tr>")
    
    for s in students:
        print s.first_name + " " + s.last_name
        out_file.write("<tr>")
        out_file.write("<td>%s %s</td>" % (s.first_name, s.last_name))
        
        
        no_quizzes = 0
        no_attempted = 0
        no_passed = 0
        
        for c in courses:       
            # other quizzes - no times taken, max score, min score, first score, most recent score, average score
            act_quizzes = Activity.objects.filter(section__course=c, baseline=False, type="quiz")
            no_quizzes += act_quizzes.count()
              
            quiz_digests = act_quizzes.values_list('digest', flat=True).distinct()
            
            quizzes = Quiz.objects.filter(quizprops__name='digest', quizprops__value__in=quiz_digests)
            
            for q in quizzes:
                qas = QuizAttempt.objects.filter(quiz=q,user=s).aggregate(user_max_score=Max('score'), max_score=Max('maxscore'))
                print qas
                
                if qas['user_max_score'] is not None:
                    no_attempted += 1
                    
                    if qas['user_max_score'] * 100/ qas['max_score'] >= threshold:
                        no_passed += 1

        out_file.write("<td>%d</td>" % no_quizzes) 
        out_file.write("<td>%d</td>" % no_attempted) 
        out_file.write("<td>%d</td>" % no_passed)   
        out_file.write("</tr>\n")        
            
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
    parser = argparse.ArgumentParser()
    parser.add_argument("--cohort_id", help="", type=int)
    parser.add_argument("--threshold", help="", type=int)
    parser.add_argument("--period", help="", choices=['project','training','cpd','op3.4-mar16'])
    parser.add_argument("--course_range", help="", choices=['all','ancpnc','anc', 'pnc'])
    args = parser.parse_args()
    run(args.cohort_id, args.threshold, args.period, args.course_range)  