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
    
    cohort_id = 23
    
    SHOW_COURSE_BREAKDOWN = False
    
    students = User.objects.filter(participant__cohort_id=cohort_id, participant__role=Participant.STUDENT).order_by('username')
    anc1 = Course.objects.filter(coursecohort__cohort_id = cohort_id, shortname='anc1-et').order_by('title')
    anc2 = Course.objects.filter(coursecohort__cohort_id = cohort_id, shortname='anc2-et').order_by('title')
    pnc = Course.objects.filter(coursecohort__cohort_id = cohort_id, shortname='pnc-et').order_by('title')
    
    date = datetime.datetime.now().strftime('%Y-%m-%d')
    output_file = os.path.join(os.path.dirname(os.path.realpath(__file__)), '..', '_output', 'hew-quiz-progress-multichoice-' + date + '.html')
    out_file = open(output_file, 'w', 'utf-8')
    
    out_file.write("<html>")
    out_file.write("<head>")
    out_file.write('<meta http-equiv="Content-Type" content="text/html;charset=utf-8" />')
    out_file.write("<style> td {text-align:center;}</style>")
    out_file.write("</head>")
    out_file.write("<body>")
    
    out_file.write("<table>")
    
    if SHOW_COURSE_BREAKDOWN:
        out_file.write("<tr>")
        out_file.write("<th>&nbsp;</th>")
        out_file.write("<th colspan=3>ANC 1</th>")
        out_file.write("<th colspan=3>ANC 2</th>")
        out_file.write("<th colspan=3>PNC</th>")
        out_file.write("<th colspan=3>Total</th>")
        out_file.write("</tr>")
    
    
    out_file.write("<tr>")
    out_file.write("<th>Student</th>")
    
    if SHOW_COURSE_BREAKDOWN:
        out_file.write("<th>No Quizzes</th>")
        out_file.write("<th>No Attempted</th>")
        out_file.write("<th>No Passed</th>")
        out_file.write("<th>No Quizzes</th>")
        out_file.write("<th>No Attempted</th>")
        out_file.write("<th>No Passed</th>")
        out_file.write("<th>No Quizzes</th>")
        out_file.write("<th>No Attempted</th>")
        out_file.write("<th>No Passed</th>")
    
    out_file.write("<th>No Quizzes</th>")
    out_file.write("<th>No Attempted</th>")
    out_file.write("<th>No Passed</th>")
    out_file.write("</tr>")
    
    for s in students:
        print s.first_name + " " + s.last_name
        out_file.write("<tr>")
        out_file.write("<td>%s %s</td>" % (s.first_name, s.last_name))
        
        anc1_no_quizzes = 0
        anc1_no_attempted = 0
        anc1_no_passed = 0
        
        for c in anc1:       
            # other quizzes - no times taken, max score, min score, first score, most recent score, average score
            quizzes = Activity.objects.filter(section__course=c, baseline=False, type="quiz")
            anc1_no_quizzes += quizzes.count()
              
            quiz_digests = quizzes.values_list('digest', flat=True).distinct()
            
            # get the quiz and all attempts by the user
            for quiz_act in quizzes:
                passed = False
                quiz = Quiz.objects.get(quizprops__value=quiz_act.digest, quizprops__name='digest')
                quiz_attempts = QuizAttempt.objects.filter(user=s,quiz=quiz)
                if quiz_attempts.count() > 0:
                    anc1_no_attempted += 1

                for qa in quiz_attempts:
                    qar = QuizAttemptResponse.objects.filter(quizattempt=qa, question__type='multichoice')
                    mc_score = QuizAttemptResponse.objects.filter(quizattempt=qa, question__type='multichoice').aggregate(user_score = Sum('score'))
                    #print mc_score['user_score']
                    #print qar.count()
                    if mc_score['user_score']*100/qar.count() >= 80.0:
                        passed = True
                        break
                if passed:
                    anc1_no_passed += 1
                    
            print "ANC1: " + str(anc1_no_passed)
        
        if SHOW_COURSE_BREAKDOWN:
            out_file.write("<td>%d</td>" % anc1_no_quizzes) 
            out_file.write("<td>%d</td>" % anc1_no_attempted) 
            out_file.write("<td>%d</td>" % anc1_no_passed) 
        
            
        anc2_no_quizzes = 0  
        anc2_no_attempted = 0
        anc2_no_passed = 0
        
        for c in anc2:       
            # other quizzes - no times taken, max score, min score, first score, most recent score, average score
            quizzes = Activity.objects.filter(section__course=c, baseline=False, type="quiz")
            anc2_no_quizzes += quizzes.count()
              
            quiz_digests = quizzes.values_list('digest', flat=True).distinct()
                
            # get the quiz and all attempts by the user
            for quiz_act in quizzes:
                passed = False
                quiz = Quiz.objects.get(quizprops__value=quiz_act.digest, quizprops__name='digest')
                quiz_attempts = QuizAttempt.objects.filter(user=s,quiz=quiz)
                
                if quiz_attempts.count() > 0:
                    anc2_no_attempted += 1
                    
                for qa in quiz_attempts:
                    qar = QuizAttemptResponse.objects.filter(quizattempt=qa, question__type='multichoice')
                    mc_score = QuizAttemptResponse.objects.filter(quizattempt=qa, question__type='multichoice').aggregate(user_score = Sum('score'))
                    #print mc_score['user_score']
                    #print qar.count()
                    if mc_score['user_score']*100/qar.count() >= 80.0:
                        passed = True
                        break
                if passed:
                    anc2_no_passed += 1
                    
            print "ANC2: " + str(anc2_no_passed)
        
        if SHOW_COURSE_BREAKDOWN:
            out_file.write("<td>%d</td>" % anc2_no_quizzes) 
            out_file.write("<td>%d</td>" % anc2_no_attempted) 
            out_file.write("<td>%d</td>" % anc2_no_passed) 
        
            
        pnc_no_quizzes = 0
        pnc_no_attempted = 0
        pnc_no_passed = 0
        
        for c in pnc:       
            # other quizzes - no times taken, max score, min score, first score, most recent score, average score
            quizzes = Activity.objects.filter(section__course=c, baseline=False, type="quiz")
            pnc_no_quizzes += quizzes.count()
              
            quiz_digests = quizzes.values_list('digest', flat=True).distinct()
                
            for quiz_act in quizzes:
                passed = False
                quiz = Quiz.objects.get(quizprops__value=quiz_act.digest, quizprops__name='digest')
                quiz_attempts = QuizAttempt.objects.filter(user=s,quiz=quiz)
                
                if quiz_attempts.count() > 0:
                    pnc_no_attempted += 1
                    
                for qa in quiz_attempts:
                    qar = QuizAttemptResponse.objects.filter(quizattempt=qa, question__type='multichoice')
                    mc_score = QuizAttemptResponse.objects.filter(quizattempt=qa, question__type='multichoice').aggregate(user_score = Sum('score'))
                    #print mc_score['user_score']
                    #print qar.count()
                    if mc_score['user_score']*100/qar.count() >= 80.0:
                        passed = True
                        break
                if passed:
                    pnc_no_passed += 1
                    
            print "PNC: " + str(pnc_no_passed)
        
        if SHOW_COURSE_BREAKDOWN:
            out_file.write("<td>%d</td>" % pnc_no_quizzes) 
            out_file.write("<td>%d</td>" % pnc_no_attempted) 
            out_file.write("<td>%d</td>" % pnc_no_passed) 

        
        no_quizzes = pnc_no_quizzes + anc1_no_quizzes + anc2_no_quizzes
        no_attempted = pnc_no_attempted + anc1_no_attempted + anc2_no_attempted
        no_passed = pnc_no_passed + anc1_no_passed + anc2_no_passed
        
        out_file.write("<td>%d</td>" % no_quizzes) 
        out_file.write("<td>%d</td>" % no_attempted) 
        out_file.write("<td>%d</td>" % no_passed)   
        out_file.write("</tr>\n")
        
        # overall for all courses
        
            
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