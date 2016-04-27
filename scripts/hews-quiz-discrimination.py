''''
Calculates the difficulty and discrimination indexes for every question in the specified courses 

Uses the algorithms for P-Score (Difficulty) and D-Score (Discrimination) defined as:

Difficulty Index

The item difficulty index is one of the most useful, and most frequently reported, item analysis statistics. It is a 
measure of the proportion of examinees who answered the item correctly; for this reason it is frequently called the 
p-value. As the proportion of examinees who got the item right, the p-value might more properly be called the item 
easiness index, rather than the item difficulty. It can range between 0.0 and 1.0, with a higher value indicating that a 
greater proportion of examinees responded to the item correctly, and it was thus an easier item.

Difficulty index (P score) = (Total true response of the item / Total responses)  x 100

Where Total responses= (True response + Wrong response + Not responded)

For a maximum discrimination between high and low achievers, the optimal levels (adjusting for guessing) are: 
Item Difficulty

    2 alternatives true and false = .75
    3 alternatives multiple-choice = .67
    4 alternatives multiple-choice = .63
    5 alternatives multiple-choice = .60

Items with difficulties less than 30 percent or more than 90 perecent definitely need attention. Such items should 
either be revised or replaced. 

Discriminating  index:

The item discrimination index is a measure of how well an item is able to distinguish between examinees who are 
knowledgeable and those who are not, or between masters and non-masters.

Total score for each individual student is calculated and arranged in descending order from highest score to lowest  
score. Upper 1/3 students are selected to include in higher group  (H) and lower  1/3 students are  selected to include 
in lower group (L). Item

 Discriminating  index is calculated by the following formula

Discriminating index (D Score) = (HT-LT / T) x 2

 HT = Number of correct responses in Upper Group,

LT = Number of correct responses in Lower Group

T= Total number of responses in both group.

Negative ID is   

Unacceptable - check item for error

0% - 24%
    

 
    

 
    

Usually unacceptable - might be approved

25% - 39%
    

 
    

 
    

Good item

40% - 100%
    

 
    

 
    

Excellent item

The maximum item discrimination difference is 100 percent. This would occur if all those in the upper group answered 
correctly and all those in the lower group answered incorrectly. Zero discrimination occurs when equal numbers in both 
groups answer correctly. Negative discrimination occurs when more students in the lower group then the upper group 
answer correctly.
'''


import json
import datetime
import os

from codecs import open

def run(): 
    
    from django.contrib.auth.models import User
    from django.db.models import Sum, Max, Min, Avg
    from django.utils.html import strip_tags
    
    from oppia.models import Activity, Course, Cohort, CourseCohort, Participant, Tracker
    from oppia.quiz.models import Quiz, Question, QuizQuestion, QuizAttempt, QuizAttemptResponse
    
    cohort_id = 23
    
    students = User.objects.filter(participant__cohort_id=cohort_id, participant__role=Participant.STUDENT).order_by('username')
    courses = Course.objects.filter(coursecohort__cohort_id = cohort_id, shortname__in=['anc1-et','anc2-et','pnc-et']).order_by('title')
    
    date = datetime.datetime.now().strftime('%Y-%m-%d')
    output_file = os.path.join(os.path.dirname(os.path.realpath(__file__)), '..', '_output', 'hew-quiz-discrimination-' + date + '.html')
    
    out_file = open(output_file, 'w', 'utf-8')
    
    out_file.write("<html>")
    out_file.write("<head>")
    out_file.write('<meta http-equiv="Content-Type" content="text/html;charset=utf-8" />')
    out_file.write("<style> td {text-align:center;} #footer { font-size:small; font-style:italic; } </style>")
    out_file.write("</head>")
    out_file.write("<body>")
    
    out_file.write("<table>")
    out_file.write("<tr>")
    out_file.write("<th>Course</th>")
    out_file.write("<th>Quiz</th>")
    out_file.write("<th>Question</th>")
    out_file.write("<th>Question Type</th>")
    out_file.write("<th>No attempts</th>")
    out_file.write("<th>No incorrect</th>")
    out_file.write("<th>No partially correct</th>")
    out_file.write("<th>No correct</th>")
    out_file.write("<th>P-score - Difficulty</th>")
    out_file.write("<th>D-Score - Discrimination</th>")
    out_file.write("</tr>")
    
    for c in courses:
        out_file.write("<tr>")
        out_file.write("<td colspan='10'>%s</td>" % title_lang(c.title,"en"))
        print "%s"  % title_lang(c.title,"en")
        print "===================================="
        out_file.write("</tr>")
        quizzes = Activity.objects.filter(section__course=c, type="quiz").exclude(section__order=0).order_by('section__order')
        #quizzes = Activity.objects.filter(section__course=c, type="quiz").order_by('section__order')
        for q in quizzes:
            
            quiz = Quiz.objects.get(quizprops__value=q.digest, quizprops__name="digest")
            out_file.write("<tr><td></td>")
            desc = strip_tags(title_lang(quiz.description,"en").replace(u'\xa0',''))
            out_file.write("<td colspan='9'>%s - %s</td>" % (title_lang(quiz.title,"en"), desc))
            print ("Processing: %s - %s"  % (title_lang(quiz.title,"en"), desc))
            out_file.write("</tr>")
            
            print q.digest
            print q.id
            
            # get questions for quiz
            questions = Question.objects.filter(quizquestion__quiz=quiz).exclude(type='description').order_by("quizquestion__order")
            for qu in questions:
                out_file.write("<tr><td colspan='2'></td>")
                title = strip_tags(title_lang(qu.title,"en").replace(u'\xa0','').replace(u'\u2019','').replace(u'\u2018','').replace(u'\xb0','').replace(u'\xba',''))
                out_file.write("<td width='35%%'>%s</td>" % title)
                out_file.write("<td>%s</td>" % qu.type)
                
                # get no attempts
                qars = QuizAttemptResponse.objects.filter(question=qu,quizattempt__user__in=students)
                
                # get no incorrect/partial/correct
                incorrect = 0
                partial = 0
                correct = 0
                
                for qar in qars:
                    if qar.score == 0:
                        incorrect += 1
                    elif qar.score == 1:
                        correct += 1
                    else:
                        partial += 1
                
                out_file.write("<td>%d</td>" % qars.count())
                out_file.write("<td>%d (%d%%)</td>" % (incorrect, incorrect*100/qars.count()))
                if qu.type == 'multichoice':
                    out_file.write("<td>-</td>")
                else: 
                    out_file.write("<td>%d (%d%%)</td>" % (partial, partial*100/qars.count()))
                out_file.write("<td>%d (%d%%)</td>" % (correct, correct*100/qars.count()))
                
                
                # calc P & D scores for question
                
                
                if qu.type == 'multichoice':
                    p_score = float(correct) / float(qars.count())
                    out_file.write("<td>%.3f</td>" % (p_score))
                else:
                    out_file.write("<td>-</td>")
                    
                
                top_third = qars.order_by('-score')[:int(qars.count()/3)]
                top_correct_count = 0
                for tt in top_third:
                    if tt.score == 1:
                        top_correct_count += 1
                
                bottom_third = qars.order_by('score')[:int(qars.count()/3)]
                bottom_correct_count = 0
                for bt in bottom_third:
                    if bt.score == 1:
                        bottom_correct_count += 1
                
                print top_third.count()
                print bottom_third.count()
                
                d_score = (top_correct_count - bottom_correct_count) * 2.0 / (top_third.count() + bottom_third.count())
                out_file.write("<td>%.3f</td>" % (d_score))
                
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