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
    START_DATE = datetime.datetime(2015,4,01,0,0,0)
    print START_DATE
    END_DATE = datetime.datetime(2016,8,31,23,59,59)
    print END_DATE
    
    tutors = User.objects.filter(participant__cohort_id=COHORT_ID, participant__role=Participant.TEACHER).order_by('username')
    
    date = datetime.datetime.now().strftime('%Y-%m-%d')
    output_file = os.path.join(os.path.dirname(os.path.realpath(__file__)), '..', '_output', 'tutor-activity-' + date + '.html')
    out_file = open(output_file, 'w', 'utf-8')
    
    out_file.write("<html>")
    out_file.write("<head>")
    out_file.write('<meta http-equiv="Content-Type" content="text/html;charset=utf-8" />')
    out_file.write("<style> td {text-align:center;} #footer { font-size:small; font-style:italic; } </style>")
    out_file.write("</head>")
    out_file.write("<body>")
    out_file.write("<h2>Tutor Monitoring Hits for %s to %s</h2>" % (START_DATE, END_DATE))
    out_file.write("<table>")
    
    out_file.write("<tr>")
    out_file.write("<th>Tutor</th>")
    out_file.write("<th>Total Hits</th>")
    out_file.write("</tr>")
    
    for t in tutors:
        print t.first_name + " " + t.last_name
        out_file.write("<tr>")
        out_file.write("<td>%s %s</td>" % (t.first_name, t.last_name))
        activity = Tracker.objects.filter(user=t, type='monitor').count()
        out_file.write("<td>%d</td>" % (activity))
        
        
        out_file.write("</tr>")
      
    out_file.write("</table>") 
    out_file.write("<div id='footer'>Report generated at %s by script %s</div>" % (datetime.datetime.now().strftime('%Y-%m-%d %H:%M'),os.path.realpath(__file__)))  
    out_file.write("</body></html>")
    out_file.close() 
    
if __name__ == "__main__":
    import django
    django.setup()
    run()