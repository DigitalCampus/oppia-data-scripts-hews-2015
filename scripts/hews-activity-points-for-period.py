'''
Calculates the activity, points, quizzes passed and media views during a particular time period 

'''

import datetime
import json
import os

from codecs import open

def run(): 
    
    from django.contrib.auth.models import User
    from django.db.models import Sum, Max, Min, Avg
    
    from oppia.models import Activity, Course, Cohort, CourseCohort, Participant, Tracker, Points

    COHORT_ID = 23
    START_DATE = datetime.datetime(2015,8,01,0,0,0)
    print START_DATE
    END_DATE = datetime.datetime(2016,5,31,23,59,59)
    print END_DATE
    
    students = User.objects.filter(participant__cohort_id=COHORT_ID, participant__role=Participant.STUDENT).order_by('username')
    #courses = Course.objects.filter(coursecohort__cohort_id = COHORT_ID, shortname__in=['anc1-et','anc2-et','pnc-et'])
    courses = Course.objects.filter(coursecohort__cohort_id = COHORT_ID)
    
    date = datetime.datetime.now().strftime('%Y-%m-%d')
    output_file = os.path.join(os.path.dirname(os.path.realpath(__file__)), '..', '_output', 'hew-activity-points-for-period-' + date + '.html')
    out_file = open(output_file, 'w', 'utf-8')
    
    out_file.write("<html>")
    out_file.write("<head>")
    out_file.write('<meta http-equiv="Content-Type" content="text/html;charset=utf-8" />')
    out_file.write("<style> td {text-align:center;} #footer { font-size:small; font-style:italic; } </style>")
    out_file.write("</head>")
    out_file.write("<body>")
    out_file.write("<h2>Activity, quiz, media and points for %s to %s</h2>" % (START_DATE, END_DATE))
    out_file.write("<h3>Courses: %s</h3>" % courses.values_list('shortname', flat=True))
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
        
        quiz_passed = Tracker.objects.filter(user=s, submitted_date__gte=START_DATE, submitted_date__lte=END_DATE, type=Activity.QUIZ, completed=True, course__in=courses).count()
        out_file.write("<td>%d</td>" % (quiz_passed))
        
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
    run()