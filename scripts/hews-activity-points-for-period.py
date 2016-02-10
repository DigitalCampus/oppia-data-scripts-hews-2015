import datetime
import json
import os

from codecs import open

def run(): 
    
    from django.contrib.auth.models import User
    from django.db.models import Sum, Max, Min, Avg
    
    from oppia.models import Activity, Course, Cohort, CourseCohort, Participant, Tracker, Points

    COHORT_ID = 23
    START_DATE = datetime.datetime(2015,12,01,0,0,0)
    print START_DATE
    END_DATE = datetime.datetime(2016,01,31,23,59,59)
    print END_DATE
    
    students = User.objects.filter(participant__cohort_id=COHORT_ID, participant__role=Participant.STUDENT).order_by('username')
    
    date = datetime.datetime.now().strftime('%Y-%m-%d')
    output_file = os.path.join(os.path.dirname(os.path.realpath(__file__)), '..', '_output', 'hew-activity-points-for-period-' + date + '.html')
    out_file = open(output_file, 'w', 'utf-8')
    
    out_file.write("<html>")
    out_file.write("<head>")
    out_file.write('<meta http-equiv="Content-Type" content="text/html;charset=utf-8" />')
    out_file.write("<style> td {text-align:center;}</style>")
    out_file.write("</head>")
    out_file.write("<body>")
    out_file.write("<h2> Activity, quiz, media and points for %s to %s</h2>" % (START_DATE, END_DATE))
    
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
        activity = Tracker.objects.filter(user=s, submitted_date__gte=START_DATE, submitted_date__lte=END_DATE).count()
        out_file.write("<td>%d</td>" % (activity))
        
        quiz_attempts = Tracker.objects.filter(user=s, submitted_date__gte=START_DATE, submitted_date__lte=END_DATE, type=Activity.QUIZ).count()
        out_file.write("<td>%d</td>" % (quiz_attempts))
        
        quiz_passed = Tracker.objects.filter(user=s, submitted_date__gte=START_DATE, submitted_date__lte=END_DATE, type=Activity.QUIZ, completed=True).count()
        out_file.write("<td>%d</td>" % (quiz_passed))
        
        media = Tracker.objects.filter(user=s, submitted_date__gte=START_DATE, submitted_date__lte=END_DATE, type=Activity.MEDIA).count()
        out_file.write("<td>%d</td>" % (media))
        
        points = Points.objects.filter(user=s, date__gte=START_DATE, date__lte=END_DATE).aggregate(total=Sum('points'))
        if points['total']:
            out_file.write("<td>%d</td>" % (points['total']))
        else: 
            out_file.write("<td>%d</td>" % (0))
        
        out_file.write("</tr>")
        
    out_file.write("</table>")   
    out_file.write("</body></html>")
    out_file.close() 
    
if __name__ == "__main__":
    import django
    django.setup()
    run()