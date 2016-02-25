import datetime
import json
import os

from codecs import open

def run(): 
    from django.contrib.auth.models import User
    from django.db.models import Sum, Max, Min, Avg
    from django.utils.html import strip_tags
    
    from oppia.models import Activity, Course, Cohort, CourseCohort, Participant, Tracker, Media
    
    cohort_id = 23
    
    students = User.objects.filter(participant__cohort_id=cohort_id, participant__role=Participant.STUDENT).order_by('username')
    
    date = datetime.datetime.now().strftime('%Y-%m-%d')
    output_file = os.path.join(os.path.dirname(os.path.realpath(__file__)), '..', '_output', 'hew-video-views-' + date + '.html')
    out_file = open(output_file, 'w', 'utf-8')
    
    out_file.write("<html>")
    out_file.write("<head>")
    out_file.write('<meta http-equiv="Content-Type" content="text/html;charset=utf-8" />')
    out_file.write("</head>")
    out_file.write("<body>")
    
    out_file.write("<table>")
    out_file.write("<tr>")
    out_file.write("<th>HEW</th>")
    out_file.write("<th>No views</th>")
    out_file.write("<th>Total time viewed</th>")
    out_file.write("</tr>")
    
    for hew in students:
        trackers = Tracker.objects.filter(type=Activity.MEDIA, user=hew)
        total_time = 0
        
        for t in trackers:
            total_time += t.time_taken
        
        out_file.write("<tr>")
        out_file.write("<td>%s %s</td>" % (hew.first_name, hew.last_name))
        out_file.write("<td>%d</td>" % trackers.count())
        out_file.write("<td>%s</td>" % datetime.timedelta(seconds=total_time))
        out_file.write("</tr>")
        
        
    
    out_file.write("</table>")   
    out_file.write("</body></html>")
    out_file.close()
    
    
    
if __name__ == "__main__":
    import django
    django.setup()
    run() 