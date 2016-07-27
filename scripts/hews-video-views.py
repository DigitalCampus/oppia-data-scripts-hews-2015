import datetime
import json
import os

from codecs import open

def run(): 
    from django.contrib.auth.models import User
    from django.db.models import Sum, Max, Min, Avg
    from django.utils.html import strip_tags
    
    from oppia.models import Activity, Course, Cohort, CourseCohort, Participant, Tracker, Media
    
    COHORT_ID = 23
    START_DATE = datetime.datetime(2015,8,01,0,0,0)
    print START_DATE
    END_DATE = datetime.datetime(2016,6,30,23,59,59)
    print END_DATE
    
    students = User.objects.filter(participant__cohort_id=COHORT_ID, participant__role=Participant.STUDENT).order_by('username')
    courses = Course.objects.filter(coursecohort__cohort_id = COHORT_ID)
    
    date = datetime.datetime.now().strftime('%Y-%m-%d')
    output_file = os.path.join(os.path.dirname(os.path.realpath(__file__)), '..', '_output', 'hew-video-views-' + date + '.html')
    out_file = open(output_file, 'w', 'utf-8')
    
    out_file.write("<html>")
    out_file.write("<head>")
    out_file.write('<meta http-equiv="Content-Type" content="text/html;charset=utf-8" />')
    out_file.write("<style> td {text-align:center;} #footer { font-size:small; font-style:italic; } </style>")
    out_file.write("</head>")
    out_file.write("<body>")
    out_file.write("<h2>Media views for %s to %s</h2>" % (START_DATE, END_DATE))
    out_file.write("<h3>Courses: %s</h3>" % courses.values_list('shortname', flat=True))
    
    out_file.write("<table>")
    out_file.write("<tr>")
    out_file.write("<th>HEW</th>")
    out_file.write("<th>No views</th>")
    out_file.write("<th>Total time viewed</th>")
    out_file.write("</tr>")
    
    for student in students:
        print student.username
        trackers = Tracker.objects.filter(type=Activity.MEDIA, user=student, submitted_date__gte=START_DATE, submitted_date__lte=END_DATE, course__in=courses)
        total_time = 0
        
        for t in trackers:
            total_time += t.time_taken
        
        out_file.write("<tr>")
        out_file.write("<td>%s %s</td>" % (student.first_name, student.last_name))
        out_file.write("<td>%d</td>" % trackers.count())
        out_file.write("<td>%s</td>" % datetime.timedelta(seconds=total_time))
        out_file.write("</tr>")
        
        
    
    out_file.write("</table>") 
    out_file.write("<div id='footer'>Report generated at %s by script %s</div>" % (datetime.datetime.now().strftime('%Y-%m-%d %H:%M'),os.path.realpath(__file__)))  
    out_file.write("</body></html>")
    out_file.close()
    
    
    
if __name__ == "__main__":
    import django
    django.setup()
    run() 