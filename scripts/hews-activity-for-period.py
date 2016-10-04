'''
Calculates the activity, points, quizzes passed and media views during a particular time period 

'''

import argparse
import datetime
import json
import os
import sys

from codecs import open

def run(cohort_id, threshold, period, course_range): 
    
    from django.contrib.auth.models import User
    from django.db.models import Sum, Max, Min, Avg
    
    from oppia.models import Activity, Course, Cohort, CourseCohort, Participant, Tracker, Points
    from oppia.quiz.models import Quiz, QuizAttempt
    
    print "Cohort:"  + str(cohort_id)
    print "Threshold: " + str (threshold)
    print "Period: " + period
    print "Course Range: " + course_range
    
    if period == 'project': 
        START_DATE = datetime.datetime(2015,4,01,0,0,0)
        END_DATE = datetime.datetime(2016,9,30,23,59,59)
    elif period == 'training':
        START_DATE = datetime.datetime(2015,4,01,0,0,0)
        END_DATE = datetime.datetime(2015,7,31,23,59,59)
    elif period == 'cpd':
        START_DATE = datetime.datetime(2015,8,01,0,0,0)
        END_DATE = datetime.datetime(2016,9,30,23,59,59)
    else:
        print "Invalid period supplied"
        sys.exit() 
    
    students = User.objects.filter(participant__cohort_id=cohort_id, participant__role=Participant.STUDENT).order_by('username')
    
    if course_range == 'ancpnc': 
        courses = Course.objects.filter(coursecohort__cohort_id = cohort_id, shortname__in=['anc1-et','anc2-et','pnc-et'])
    elif course_range =='all': 
        courses = Course.objects.filter(coursecohort__cohort_id = cohort_id)
    else:
        print "Invalid course range supplied"
        sys.exit()
    
    filename = 'hew-activity-' + period + '-' + course_range + '-' + str(threshold) + '.html'
    output_file = os.path.join(os.path.dirname(os.path.realpath(__file__)), '..', '_output', filename)
    out_file = open(output_file, 'w', 'utf-8')
    
    out_file.write("<html>")
    out_file.write("<head>")
    out_file.write('<meta http-equiv="Content-Type" content="text/html;charset=utf-8" />')
    out_file.write("<style> td {text-align:center;} #footer { font-size:small; font-style:italic; } </style>")
    out_file.write("</head>")
    out_file.write("<body>")
    out_file.write("<h2>Activity, quiz, media and points for %s to %s</h2>" % (START_DATE.strftime('%d-%b-%Y'), END_DATE.strftime('%d-%b-%Y')))
    out_file.write("<h3>Courses: %s</h3>" % ','.join(courses.values_list('shortname', flat=True)))
    out_file.write("<h3>Quiz Pass Threshold: %d%%</h3>" % threshold)
    out_file.write("<table>")
    
    out_file.write("<tr>")
    out_file.write("<th>Student</th>")
    out_file.write("<th>Total Activity</th>")
    out_file.write("<th>Quiz activity</th>")
    out_file.write("<th>Quizzes passed</th>")
    out_file.write("<th>Media Views</th>")
    out_file.write("<th>Points</th>")
    out_file.write("</tr>")
    
    for s in students:
        print s.first_name + " " + s.last_name
        out_file.write("<tr>")
        out_file.write("<td>%s %s</td>" % (s.first_name, s.last_name))
        activity = Tracker.objects.filter(user=s, submitted_date__gte=START_DATE, submitted_date__lte=END_DATE, course__in=courses).count()
        out_file.write("<td>%d</td>" % (activity))
        
        quiz_attempts = Tracker.objects.filter(user=s, submitted_date__gte=START_DATE, submitted_date__lte=END_DATE, type=Activity.QUIZ, course__in=courses).count()
        out_file.write("<td>%d</td>" % (quiz_attempts))
        
        '''
        if (PASS_THRESHOLD >= 80):
            quiz_passed = Tracker.objects.filter(user=s, submitted_date__gte=START_DATE, submitted_date__lte=END_DATE, type=Activity.QUIZ, completed=True, course__in=courses).count()
            out_file.write("<td>%d</td>" % (quiz_passed))
        else:
        '''
        no_passed = 0
        no_quizzes = 0
        
        for c in courses:       
            act_quizzes = Activity.objects.filter(section__course=c, baseline=False, type="quiz")
              
            quiz_digests = act_quizzes.values_list('digest', flat=True).distinct()
            
            quizzes = Quiz.objects.filter(quizprops__name='digest', quizprops__value__in=quiz_digests)
            no_quizzes += quizzes.count()
            for q in quizzes:
                qas = QuizAttempt.objects.filter(quiz=q,user=s, submitted_date__gte=START_DATE, submitted_date__lte=END_DATE ).aggregate(user_max_score=Max('score'), max_score=Max('maxscore'))
                
                if qas['user_max_score'] is not None:                        
                    if qas['user_max_score'] * 100/ qas['max_score'] >= threshold:
                        no_passed += 1
                        
        out_file.write("<td>%d/%d</td>" % (no_passed, no_quizzes))  
        
        media = Tracker.objects.filter(user=s, submitted_date__gte=START_DATE, submitted_date__lte=END_DATE, type=Activity.MEDIA, course__in=courses).count()
        out_file.write("<td>%d</td>" % (media))
        
        points = Points.objects.filter(user=s, date__gte=START_DATE, date__lte=END_DATE, course__in=courses).aggregate(total=Sum('points'))
        if points['total']:
            out_file.write("<td>%d</td>" % (points['total']))
        else: 
            out_file.write("<td>%d</td>" % (0))
        
        out_file.write("</tr>")
      
    out_file.write("</table>") 
    out_file.write("<div id='footer'>Report generated at %s by script %s</div>" % (datetime.datetime.now().strftime('%Y-%m-%d %H:%M'),os.path.realpath(__file__)))  
    out_file.write("</body></html>")
    out_file.close() 
    
if __name__ == "__main__":
    import django
    django.setup()
    parser = argparse.ArgumentParser()
    parser.add_argument("--cohort_id", help="", type=int)
    parser.add_argument("--threshold", help="", type=int)
    parser.add_argument("--period", help="", choices=['project','training','cpd'])
    parser.add_argument("--course_range", help="", choices=['all','ancpnc'])
    args = parser.parse_args()
    run(args.cohort_id, args.threshold, args.period, args.course_range) 