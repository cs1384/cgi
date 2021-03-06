#!/usr/local/bin/python

import cgi, cgitb
import subprocess
import sys
import random
import os

class Entry:
    def __init__(self, vote, aid, qid, content):
        self.vote = vote
        self.qid = qid
        self.aid = aid
        self.content = content

cgitb.enable()
form = cgi.FieldStorage()

#redirect to the set up main page
if not form.getvalue('action'):
    print 'Location: http://cs.nyu.edu/cgi-bin/cgiwrap/~ytl264/tin.cgi?action=list'

print "Content-type:text/html\r\n\r\n"
print '<html>'
print '<head>'
print '<title>ytl264</title>'
print '</head>'
print '<body>'
print '<h2>TIN - Open Sourse Tool HW3 <<a href="http://cs.nyu.edu/cgi-bin/cgiwrap/~ytl264/tin.cgi"> main </a> : <a href="http://cs.nyu.edu/cgi-bin/cgiwrap/~ytl264/tin.cgi?action=list&uid=ytl264"> ytl264 </a>></h2>'



action = form.getvalue('action')

if action == 'list':
    if not form.getvalue('uid'):
        cmd = ['/home/ytl264/public_html/cgi-bin/question', 'list']
    else: 
        uid = form.getvalue('uid')
        cmd = ['/home/ytl264/public_html/cgi-bin/question', 'list', uid]
    proc = subprocess.Popen(cmd, stdout=subprocess.PIPE)
    print '<ul style="font-size:20px;">'
    for line in proc.stdout:
        q = line.split('/')
        print '<li style="height:5px;">'
        print '<a href="http://cs.nyu.edu/cgi-bin/cgiwrap/~ytl264/tin.cgi?action=view&uid=' + q[0] + '&qname=' + q[1] + '">'
        print line
        print '</a>'
        print '</li>'
        print '<br>'
    print '</ul>'
    print '<ul style="font-size:20px;height:50px;">'
    print '<a href="http://cs.nyu.edu/cgi-bin/cgiwrap/~ytl264/tin.cgi?action=create">'
    print 'Add question' 
    print '</a>'
    print '</ul>'

elif action == 'create':
    if not form.getvalue('submit'):
        print '<form method="post" action="http://cs.nyu.edu/cgi-bin/cgiwrap/~ytl264/tin.cgi">'
        print '<div style="width:30%;height:30px">'
        print 'Question Id: '
        print '<input style="width:78%;height:80%;"type="text" name="name">'
        print '</div>'
        print '<div style="width:30%;height:70px;">'
        print '<textarea style="font-size:20px;height:100%;width:100%;" name="question" align="top">'
        print "What is your question?"
        print '</textarea>'
        print '</div>'
        print '<div style="height:35px;margin:10px;">'
        print '<input type="hidden" name="action" value="create">'
        print '<button type="button" style="height:100%;" onclick="history.go(-1)">Cancel</button>'
        print '<input style="height:100%;"type="submit" name="submit" value="Submit">'
        print '</div>'
        print '</form>'
    else:
        question = form.getvalue('question')
        #print question
        if not form.getvalue('name'):
            while True:
                rand =  int(random.random()*1000000)
                name = 'q' + str(rand)
                path = '/home/ytl264/.question/questions/' + name
                #print path
                if not os.path.exists(path):
                    break
        else:
            name = form.getvalue('name')
        #print name
        cmd = ['/home/ytl264/public_html/cgi-bin/question', 'create', name, question]
        proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE) 
        std = proc.communicate()
        if proc.returncode != 0:
            print std[1]
            print '<button type="button" onclick="history.go(-1)">Back</button>'
        else:
            print 'Question added!'
            print '<button type="button" onclick="location.href=\'http://cs.nyu.edu/cgi-bin/cgiwrap/~ytl264/tin.cgi?action=list&uid=ytl264\'">Confirm</button>'

elif action == 'view':
    if not form.getvalue('uid') or not form.getvalue('qname'):
        print 'No valid question id specified!'
        print '<button type="button" onclick="history.go(-1)">Back</button>'     
    else:
        uid = form.getvalue('uid')
        qname = form.getvalue('qname')
        qid = uid + '/' + qname
        if form.getvalue('vote'):
            vote = form.getvalue('vote').lower()
            if not form.getvalue('aid'):
                #qid = form.getvalue('qid').strip(' \t\n\r').lstrip('@')
                cmd = ['/home/ytl264/public_html/cgi-bin/question', 'vote', vote, qid]
                proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            else:
                #qid = form.getvalue('qid').strip(' \t\n\r').lstrip('@')
                aid = form.getvalue('aid').strip(' \t\n\r')
                cmd = ['/home/ytl264/public_html/cgi-bin/question', 'vote', vote, qid, aid]
                proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        cmd = ['/home/ytl264/public_html/cgi-bin/question', 'view', qid]
        proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        content = []
        for line in proc.stdout:
            content.append(line)
            #print line
            #print '<br>'
        std = proc.communicate()
        #print "==================="
        if proc.returncode != 0:
            print std[1]
            print '<button type="button" onclick="history.go(-1)">Back</button>'
        else:
            head = True
            division = True
            body = ''
            token = []
            list = []
            for line in content:
                if head and division:
                    token = line.strip(' \t\n\r').split(' ')
                    if len(token) > 2:
                        for i in range(2,len(token)):
                            token[1] = token[1] + ' ' + token[i]
                    division = False
                elif head:
                    if '====' in line:
                        q = Entry(token[0], '', token[1], body)
                        body = ''
                        division = True
                        head = False
                    else:
                        body = body + line
                elif division:
                    temp = line.strip(' \t\n\r').split('@')
                    token = temp[0].split(' ')
                    if len(token) > 2:
                        for i in range(2,len(token)-1):
                            token[1] = token[1] + ' ' + token[i]
                    token[2] = '@' + temp[1]
                    division = False
                else:
                    if '====' in line:
                        ans = Entry(token[0], token[1], token[2], body)
                        body = ''
                        list.append(ans)
                        division = True
                    else:
                        body = body + line
            print '<div style="margin:0 0 0 1%;font-size:30px;width:30%;">'
            print q.content
            #print '<div style="float:left;font-size:15px;">'
            print '<span style="font-size:15px;line-height:30px">'
            print ' - ' + q.qid
            print '</span>'
            #print '</div>'
            print '</div>'
            print '<div style="height:30px;width:30%;line-height:30px;">'
            print '<form method="get">'
            print '<input type="hidden" name="action" value="view">'
            print '<input type="hidden" name="uid" value="'+ uid +'">'
            print '<input type="hidden" name="qname" value="'+ qname +'">'
            print '<input style="float:right;height:100%;width:20%;" type="submit" name="vote" value="Down">'
            print '<input style="float:right;height:100%;width:20%;" type="submit" name="vote" value="Up">'
            print '</form>'
            print '<div style="text-align:center;float:right;height:100%;width:15%;line-height:15px;">'
            if int(q.vote) >= 0:
                print '+' + q.vote
            else:
                print q.vote
            print '</div>'
            print '</div>'                 
            print '<div style="height:5px;width:28%;margin:0 0 5px 1%;border-bottom:2px solid black"></div>'               

            list = sorted(list, key=lambda Entry: Entry.vote, reverse=True)

            for entry in list:
                print '<div style="margin:5px 0 0 1%;font-size:25px;width:30%;">'
                print entry.content
                print '<span style="font-size:15px;line-height:25px;">'
                print ' - ' + entry.aid
                print entry.qid
                print '</span>'
                print '</div>'
                print '<div style="height:30px;width:30%;line-height:30px;">'
                print '<form method="post" action="http://cs.nyu.edu/cgi-bin/cgiwrap/~ytl264/tin.cgi">'
                print '<input type="hidden" name="action" value="view">'
                print '<input type="hidden" name="aid" value="'+ str(entry.aid) +'">'
                print '<input type="hidden" name="uid" value="'+ uid +'">'
                print '<input type="hidden" name="qname" value="'+ qname +'">'  
                print '<input style="float:right;height:100%;width:20%;" type="submit" name="vote" value="Down">'
                print '<input style="float:right;height:100%;width:20%;" type="submit" name="vote" value="Up">'
                print '</form>'
                print '<div style="text-align:center;float:right;height:100%;width:15%;line-height:15px;">'
                if int(entry.vote) >= 0:
                    print '+' + entry.vote
                else:
                    print entry.vote
                print '</div>'
                print '</div>'                 
                print '<div style="height:5px;width:28%;margin:0 0 5px 1%;border-bottom:2px solid rgb(180, 180, 180)"></div>'           
            print '<br>'
            print '<ul style="font-size:20px;height:50px;">'
            print '<a href="http://cs.nyu.edu/cgi-bin/cgiwrap/~ytl264/tin.cgi?action=answer&uid='+uid+'&qname='+qname+'">'
            print 'Add answer' 
            print '</a>'
            print '</ul>'

elif action == 'answer':
    if not form.getvalue('submit'):
        uid = form.getvalue('uid')
        qname = form.getvalue('qname')
        print '<form method="post" action="http://cs.nyu.edu/cgi-bin/cgiwrap/~ytl264/tin.cgi">'
        print '<div style="width:30%;height:30px">'
        print 'Answer Id: '
        print '<input style="width:78%;height:80%;"type="text" name="name">'
        print '</div>'
        print '<div style="width:30%;height:70px;">'
        print '<textarea style="font-size:20px;height:100%;width:100%;" name="answer" align="top">'
        print "Answer here."
        print '</textarea>'
        print '</div>'
        print '<div style="height:35px;margin:10px;">'
        print '<input type="hidden" name="action" value="answer">'
        print '<input type="hidden" name="uid" value="'+str(uid)+'">'
        print '<input type="hidden" name="qname" value="'+str(qname)+'">'
        print '<button type="button" style="height:100%;" onclick="history.go(-1)">Cancel</button>'
        print '<input style="height:100%;"type="submit" name="submit" value="Submit">'
        print '</div>'
        print '</form>'
    else:
        uid = form.getvalue('uid')
        qname = form.getvalue('qname')
        qid = uid + '/' + qname
        answer = form.getvalue('answer')
        if not form.getvalue('name'):
            while True:
                rand =  int(random.random()*1000000)
                name = 'a' + str(rand)
                path = '/home/ytl264/.question/answers/'+uid+'/'+qname+'/' + name
                #print path
                if not os.path.exists(path):
                    break
        else:
            name = form.getvalue('name')
        cmd = ['/home/ytl264/public_html/cgi-bin/question', 'answer', qid, name, answer]
        proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE) 
        std = proc.communicate()
        if proc.returncode != 0:
            print std[1]
            print '<button type="button" onclick="history.go(-1)">Back</button>'
        else:
            print 'Answer added!'
            print '<button type="button" onclick="location.href=\'http://cs.nyu.edu/cgi-bin/cgiwrap/~ytl264/tin.cgi?action=view&uid='+uid+'&qname='+qname+'\'">Confirm</button>'

print '</body>'
print '</html>'

