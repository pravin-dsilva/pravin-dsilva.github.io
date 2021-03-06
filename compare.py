from __future__ import division

import requests, json
from shutil import copyfile
from yattag import Doc, indent


from datetime import datetime
startTime = datetime.now()

copyfile("./helper.js", "/var/www/html/helper.js")


def getResultImage(res) :
    ur = "https://builds.apache.org/static/53471590/images/48x48/{0}.png"
    if res == "UNSTABLE" :
        return ur.format('yellow')
    if res == "SUCCESS" :
        return ur.format('blue')
    if res == "FAILURE" :
        return ur.format('red')
    if res == "ABORTED" :
        return ur.format('aborted')
        


def getFailures(url, os ,job_name) :
    totalTests = 0
    skippedTests = 0
    failedTests = 0
    testNames = []
    testErrs = []
    try:
        testresult = requests.get(url,auth=(user, password))
        testresult = json.loads(testresult.text,strict=False)
        if job_name == 'hadoop':
            for test in testresult['suites'] :
                for case in test['cases'] :
                    totalTests += 1
                    if case['skipped'] ==  True: 
                        skippedTests += 1
                    if case['status'] != 'PASSED' and case['status'] != 'SKIPPED' and case['status'] != 'FIXED' :
                        testNames.append(case['className']+"."+case['name'])
                        failedTests +=1
                        if case['errorDetails'] :
                            testErrs.append(case['errorDetails'][:400])
                        else :
                            testErrs.append(case['errorStackTrace'][:400])
        else:
            for test in testresult['suites'] :
                if test['enclosingBlockNames'][1] == os:
                    for case in test['cases'] :
                        totalTests += 1
                        if case['skipped']  ==  True: 
                            skippedTests += 1
                        if case['status'] != 'PASSED' and case['status'] != 'SKIPPED' and case['status'] != 'FIXED' :
                            testNames.append(case['className']+"."+case['name'])
                            failedTests +=1
                            if case['errorDetails'] :
                                testErrs.append(case['errorDetails'][:400])
                            else :
                                testErrs.append(case['errorStackTrace'][:400])
        return testNames, testErrs, totalTests,  failedTests, skippedTests
    except:
        return  "Error: Unable to fetch results!", "Unable to fetch results!", "Unable to fetch results!", "Unable to fetch results!", "Unable to fetch results!",    
   
    
    
doc, tag, text = Doc().tagtext()
user="pravin"
password="pravin123456"

jobs = []
summary = {'ppcubuntu16' : [], 'ppcrhel7' : [],'x86ubuntu16' : [], 'x86rhel7' : [] }
summary_name = ['ppc ubuntu16', 'x86 ubuntu16', 'ppc rhel7','x86 rhel7']
xserver_url="http://10.88.67.123:7070"
job_url="/job/"
a_j="/api/json"
req=xserver_url+a_j
resp = requests.get(req,auth=(user, password))

for job in resp.json()['jobs'] :
    jobs.append(job['name'])
#jobs.append("accumulo")

def getBuild(x86_resp, job_name):
    all_builds = x86_resp['builds']
    i = 0
    build_url = ""
    build_url = all_builds[0]['url']
    for build in all_builds:
        if (i < 5):
            try:
                build_age = 0
                environment = ['ppcub16', 'x86ub16', 'ppcrh7', 'x86rh7']
                x = set([])
                builds_status_resp = requests.get(build['url'] + a_j + "", auth=(user, password))
                if builds_status_resp.json()['result'] != 'ABORTED' and  builds_status_resp.json()['building'] == False :
                    builds_job_resp = requests.get(build['url'] + 'testReport' + a_j + "", auth=(user, password))
                    builds_job_resp = json.loads(builds_job_resp.text, strict=False)
                    build_date = builds_status_resp.json()['timestamp'] 
                    converted_date = datetime.fromtimestamp(round(build_date/ 1000))
                    current_time_utc = datetime.utcnow()
                    build_age = (current_time_utc - converted_date).days
                    if job_name == 'hadoop' and build_age < 7 :
                        return build['url']
                    else:
                        for test in builds_job_resp['suites']:
                            for env in environment:
                                if test['enclosingBlockNames'][1] == env:
                                    x.add(env)
                        if len(x) == 4 and build_age < 7 :
                            return build['url']
            except:
                continue
                
        i = i + 1
    return  build_url 
def getResult(total_count ,failed_count):
    if total_count == 0:
        result = 'FAILURE'
    if failed_count == 0 and total_count > 0:
        result = 'SUCCESS'  
    if failed_count > 0  and total_count > 0:
        result = 'UNSTABLE'
    return result
        
with tag('html'):
    
    with tag('head'):
        with tag('script',src="https://ajax.googleapis.com/ajax/libs/jquery/3.3.1/jquery.min.js"):
            text()
        with  tag('link', rel="stylesheet", href="https://maxcdn.bootstrapcdn.com/bootstrap/3.3.7/css/bootstrap.min.css", integrity="sha384-BVYiiSIFeK1dGmJRAkycuHAHRg32OmUcww7on3RYdg4Va+PmSTsz/K68vbdEjh4u" ,crossorigin="anonymous"):
            text()
        with  tag('link', rel="stylesheet",  href="https://maxcdn.bootstrapcdn.com/bootstrap/3.3.7/css/bootstrap-theme.min.css", integrity="sha384-rHyoN1iRsVXV4nD0JutlnGaslCJuC7uwjduW9SVrLvRYooPp2bWYgmgJQIXwl/Sp" ,crossorigin="anonymous"):
            text()
        with  tag('script', src="https://maxcdn.bootstrapcdn.com/bootstrap/3.3.7/js/bootstrap.min.js", integrity="sha384-Tc5IQib027qvyjSMfHjOMaLkfuWVxZxUPnCJA7l2mCWNIpG9mGCD8wGNIcPD7Txa", crossorigin="anonymous"):
            text()
        with tag('script', src='helper.js') :
			text('function hideAll(){console.log("hideAll")}function showme(e){console.log("showme");var l,n=e.substring(7),o=document.getElementsByName("data");for(l=0;l<o.length;l++)o[l].style.display="none";var t=document.getElementsByName("summary");for(l=0;l<t.length;l++)t[l].style.display="none";document.getElementById(n).style.display="block"}')
        with tag('style'):
			text('table, th, td { vertical-align:top; padding: 3px} table {table-layout:fixed} td {word-wrap:break-word} .bs-callout { padding: 5px; margin: 5px 0; border: 1px solid #eee; border-left-width: 5px; border-radius: 3px; font-weight:normal; }.bs-callout-info {border-left-color: #5bc0de;}')
 
    with tag('body'):
        with tag('div',klass='page-header'):
            with tag('ul', klass="nav nav-pills"):
                with tag('li', role="presentation"):
                    with tag('a', style="font-weight:bold", href='#', id='anchor_ppcx86', onclick="showme(this.id);"):
                        text('FULL SUMMARY')
                for key in summary_name:
                    name = key.replace(" ", "")
                    with tag('li', role="presentation"):
                        with tag('a', style="font-weight:bold", href='#', id='anchor_'+name, onclick="showme(this.id);"):
                            text(key.upper())
                with tag('p', role="presentation", align="right",style="color:grey" ):
                    utcdate = datetime.utcnow().strftime("%d-%m-%Y %H:%M UTC")
                    text("Date: {0}".format(utcdate))
        
        with tag('div', klass="col-sm-2 col-md-2 sidebar",style='table-cell'):
            with tag('div', klass="list-group"):
                with tag('a', href='#', klass='list-group-item list-group-item-action active'):
                    text('Packages')
                for job in jobs :
                    #job_display_name = str(job).upper().replace('PIPE','')
                    with tag('a', href='#', id='anchor_'+job, klass="list-group-item list-group-item-action", onclick="showme(this.id);"):
                        j = str(job)
                        j = j.upper()
                        text(j)
            
        with tag('div',style="display: table-cell"):
            for job in jobs :
                ppcubuntu16summary = {}
                x86ubuntu16summary = {}
                x86rhel7summary = {}
                ppcrhel7summary = {}
                x86rhel7summary['testErrorName'], ppcubuntu16summary['testErrorName'], x86ubuntu16summary['testErrorName'], x86rhel7_testErrs,  ppcubuntu16_testErrs, ppcrhel7_testErrs, x86ubuntu16_testErrs, ppcrhel7summary['testErrorName']= [], [], [], [], [], [], [], []
                
                
                #cheat to exclude

                job_display_name = str(job).upper()
                print "Procesing Job : " + job
                x86_job = xserver_url + job_url + job + a_j
                x86_resp = requests.get(x86_job,auth=(user, password)).json()
                if 'lastCompletedBuild' not in x86_resp.keys() or not x86_resp['lastCompletedBuild']:
                    continue  
                x86_last_builds = x86_resp['builds']
                
                buildUrl = getBuild(x86_resp, job)
                x86_lastBuild=requests.get(buildUrl+a_j,auth=(user, password)).json()
                original_build_url = buildUrl
                if job == "hadoop":
                    buildUrl = original_build_url + "label=ppcub16/"   
                ppcubuntu16summary['testErrorName'], ppcubuntu16summary['testErrorDesc'] , ppcubuntu16summary['totalCount'], ppcubuntu16summary['failedCount'], ppcubuntu16summary['skippedCount'] = getFailures(buildUrl+'testReport'+a_j, 'ppcub16',job)
                if job == "hadoop":
                    buildUrl = original_build_url + "label=master/"
                ppcrhel7summary['testErrorName'], ppcrhel7summary['testErrorDesc'], ppcrhel7summary['totalCount'], ppcrhel7summary['failedCount'], ppcrhel7summary['skippedCount'] = getFailures(buildUrl+'testReport'+a_j, 'ppcrh7',job)
                if job == "hadoop":
                    buildUrl = original_build_url + "label=x86ub16/"
                x86ubuntu16summary['testErrorName'], x86ubuntu16summary['testErrorDesc'], x86ubuntu16summary['totalCount'], x86ubuntu16summary['failedCount'], x86ubuntu16summary['skippedCount']= getFailures(buildUrl+'testReport'+a_j, 'x86ub16',job)
                if job == "hadoop":
                    buildUrl = original_build_url + "label=x86rh7/"
                x86rhel7summary['testErrorName'], x86rhel7summary['testErrorDesc'], x86rhel7summary['totalCount'], x86rhel7summary['failedCount'], x86rhel7summary['skippedCount'] = getFailures(buildUrl+'testReport'+a_j, 'x86rh7',job)
           
                ppcubuntu16summary['name'] = job_display_name
                ppcubuntu16summary['job'] = job
         
                ppcrhel7summary['name'] = job_display_name
                ppcrhel7summary['job'] = job    

                x86ubuntu16summary['name'] = job_display_name
                x86ubuntu16summary['job'] = job

                x86rhel7summary['name'] = job_display_name
                x86rhel7summary['job'] = job
                
                ppcubuntu16summary['result'] = getResult(ppcubuntu16summary['totalCount'], ppcubuntu16summary['failedCount'])
                ppcrhel7summary['result']  = getResult(ppcrhel7summary['totalCount'], ppcrhel7summary['failedCount'])
                x86ubuntu16summary['result'] = getResult(x86ubuntu16summary['totalCount'], x86ubuntu16summary['failedCount'])
                x86rhel7summary['result'] = getResult(x86rhel7summary['totalCount'], x86rhel7summary['failedCount'])
  
                environment = [ppcubuntu16summary,  x86ubuntu16summary,ppcrhel7summary, x86rhel7summary]
                with tag('div', id=job, name='data', klass="panel panel-info" ,style="font-weight:bold;display:none;"):
                    with tag('div', klass="panel-heading",style="font-weight:bold;"):
                        text(job.upper())
                    with tag('div', klass='panel-body') :
                        for action in x86_lastBuild['actions'] :
                            if action and action['_class'] == "hudson.plugins.git.util.BuildData" :
                                revHash = action['lastBuiltRevision']['branch'][0]['SHA1']
                                revName = action['lastBuiltRevision']['branch'][0]['name']
                                build_date  = datetime.fromtimestamp(round(x86_lastBuild['timestamp'] / 1000)).strftime("%d-%m-%Y %H:%M UTC")  
                                with tag('div', klass="bs-callout bs-callout-info"):
                                    with tag('div') :
                                        with tag('b'):
                                            text('Branch Details:')
                                        text( ' {0}'.format(revName))
                                        
                                    with tag('div') :
                                        with tag('b'):
                                            text('Last Revision: ')
                                        text('{0}'.format(revHash))
                                    with tag('div') :
                                        with tag('b'):
                                            text('Last Run: ')
                                        text('{0}'.format(build_date))
                                break
                        with tag('table' ,width="100%" ,klass="table table-striped",style="font-size:13"):
                            with tag('thead'):
                                #header
                                with tag('tr'):
                                    with tag('th', width="10%"):
                                        text('')
                                    with tag('th'):
                                        text('PPC UBUNTU16')
                                    with tag('th'):
                                        text('X86 UBUNTU16')
                                    with tag('th'):
                                        text('PPC RHEL7')
                                    with tag('th'):
                                        text('X86 RHEL7')
                                          
                              
                                #summary
                            with tag('tbody'):
                                with tag('tr'):
                                    with tag('td'):
                                        text('Summary')
                                    for envDetail in environment:
                                        with tag('td'):
                                                with tag('div') :
                                                            text('Total Count : {0}'.format(envDetail['totalCount']))
                                                with tag('div') :
                                                            text('Failed Count : {0}'.format(envDetail['failedCount']))
                                                with tag('div') :
                                                            text('Skipped Count : {0}'.format(envDetail['skippedCount']))
                   
                                #Status
                                with tag('tr'):
                                    with tag('td'):
                                        text('Result')
                                    for envDetail in environment:
                                        with tag('td'):
                                            with tag('img', src=getResultImage(envDetail['result']),align='top',style="width: 16px; height: 16px;"):
                                                    text()
                                            text(envDetail['result'])
                                
                                        
                                #Failures
                                with tag('tr'):
                                    with tag('td'):
                                        text('Failures')
                                    for envDetail in environment:   
                                        with tag('td') :
                                            with tag('ol',style="padding-left: 1.0em"):
                                                for t in envDetail['testErrorName'] :
                                                    with tag('div'):
                                                        with tag('li'):
                                                            text(t)
                                                                                            
                                #Description
                                with tag('tr'):
                                    with tag('td'):
                                        text('Description')
                                    for envDetail in environment:                                        
                                        with tag('td' ) :
                                            with tag('ol',style="padding-left: 1.0em"):
                                                for t in envDetail['testErrorDesc'] :
                                                    with tag('div'):
                                                        with tag('li'):
                                                            text(t)
                                                                                            

                                #Unique Failures
                                with tag('tr'):
                                    with tag('td', style="word-wrap: break-word;min-width: 160px;max-width: 220px;"):
                                        text('Unique Failures')
                                    with tag('td', style="word-wrap: break-word;min-width: 160px;max-width: 220px;"):
                                        result = [x for x in ppcubuntu16summary['testErrorName'] if x not in x86ubuntu16summary['testErrorName']]
                                        ppcubuntu16summary['unique'] = len(result)
                                        with tag('ol',style="padding-left: 1.0em"):
                                            for t in result :
                                                with tag('li'):
                                                    with tag('div'):
                                                        text(t)
                                    with tag('td', style="word-wrap: break-word;min-width: 160px;max-width: 220px;"):
                                        result = [x for x in x86ubuntu16summary['testErrorName'] if x not in ppcubuntu16summary['testErrorName']] 
                                        x86ubuntu16summary['unique'] = len(result)
                                        with tag('ol',style="padding-left: 1.0em"):
                                            for t in result :
                                                with tag('li'):
                                                    with tag('div'):
                                                        text(t)                                                        
                                    with tag('td', style="word-wrap: break-word;min-width: 160px;max-width: 220px;"):
                                        result = [x for x in ppcrhel7summary['testErrorName'] if x not in x86rhel7summary['testErrorName']]
                                        ppcrhel7summary['unique'] = len(result)
                                        with tag('ol',style="padding-left: 1.0em"):
                                            for t in result :
                                                with tag('li'):
                                                    with tag('div'):
                                                        text(t)

                                    with tag('td', style="word-wrap: break-word;min-width: 160px;max-width: 220px;"):
                                        result = [x for x in x86rhel7summary['testErrorName'] if x not in ppcrhel7summary['testErrorName']]
                                        x86rhel7summary['unique'] = len(result)
                                        with tag('ol',style="padding-left: 1.0em"):
                                            for t in result :
                                                with tag('li'):
                                                    with tag('div'):
                                                        text(t)
             
               
                summary['ppcubuntu16'].append(ppcubuntu16summary)
                summary['ppcrhel7'].append(ppcrhel7summary)
                summary['x86ubuntu16'].append(x86ubuntu16summary)
                summary['x86rhel7'].append(x86rhel7summary)
             
            for key in summary:
 
                disp = 'none'
                with tag('div',  klass="panel panel-info" , id=key, name='summary', style="font-weight:bold;font-size:12;display:"+disp):
                    with tag('div', klass="panel-heading") :
                        with tag('div', klass="panel-title") :
                            keyname = key[:3] + ' ' + key[3:]
                            text(keyname.upper()+' SUMMARY')
                    with tag('table', klass='table table-striped' ,style="font-size:14"):
                        with tag('tbody'):
                            #header
                            with tag('tr'):
                                with tag('th', ):
                                    text('Package Name')
                                with tag('th'):
                                    text('Result')
                                with tag('th'):
                                    text('')
                                with tag('th'):
                                    text('')
                            for summary_detail in summary[key]:
                                with tag('tr'):
                                    with tag('td'):
                                        with tag('a', href='#', id='anchor_'+summary_detail['job'], onclick="showme(this.id);"):
                                            text(summary_detail['name'])
                                    with tag('td'):
                                        with tag('img', src=getResultImage(summary_detail['result']),align='top',style="width: 16px; height: 16px;"):
                                            text()
                                        if summary_detail['result'] != "SUCCESS" and summary_detail['result'] != "ABORTED":
                                            text(str(summary_detail['failedCount']) + " (" + str(summary_detail['unique']) + ")")
                                    
                                    
                    
            #full summary
            with tag('div', klass="panel panel-info" , id='ppcx86', name='summary', style="display:block;font-weight:bold"):
                with tag('div', klass="panel-heading") :
                    with tag('div', klass="panel-title") :
                        text('FULL SUMMARY')
                with tag('table',klass="table table-striped"):
                    with tag('tbody'):
                        #header
                        with tag('tr'):
                            with tag('th'):
                                text()

                        with tag('tr'):
                            with tag('th'):
                                text('Package Name')
                            with tag('th'):
                                text('PPC UBUNTU16')
                            with tag('th'):
                                text('x86 UBUNTU16')
                            with tag('th'):
                                text('PPC RHEL7')
                            with tag('th'):
                                text('x86 RHEL7')

                       
                        for ppcubuntu16_detail,x86ubuntu16_detail,ppcrhel7_detail,x86rhel7_detail in zip(summary['ppcubuntu16'],summary['x86ubuntu16'],summary['ppcrhel7'],summary['x86rhel7']):
                            with tag('tr'):
                                with tag('td'):
                                    with tag('a', href='#', id='anchor_'+ppcubuntu16_detail['job'], onclick="showme(this.id);"):
                                        text(ppcubuntu16_detail['name'])
                                with tag('td'):
                                    with tag('img', src=getResultImage(ppcubuntu16_detail['result']),align='top',style="width: 16px; height: 16px;"):
                                        text()
                                    if ppcubuntu16_detail['result'] != "SUCCESS" and ppcubuntu16_detail['result'] != "SUCCESS":
                                        text(str(ppcubuntu16_detail['failedCount']) + " (" + str(ppcubuntu16_detail['unique']) + ")")
                                with tag('td'):
                                    with tag('img', src=getResultImage(x86ubuntu16_detail['result']),align='top',style="width: 16px; height: 16px;"):
                                        text()
                                    if x86ubuntu16_detail['result'] != "SUCCESS" and x86ubuntu16_detail['result'] != "ABORTED":
                                        text(str(x86ubuntu16_detail['failedCount']) + " (" + str(x86ubuntu16_detail['unique']) + ")")
                                with tag('td'):
                                    with tag('img', src=getResultImage(ppcrhel7_detail['result']),align='top',style="width: 16px; height: 16px;"):
                                        text()
                                    if ppcrhel7_detail['result'] != "SUCCESS" and ppcrhel7_detail['result'] != "ABORTED":
                                        text(str(ppcrhel7_detail['failedCount'])  + " (" + str(ppcrhel7_detail['unique']) + ")") 
                                with tag('td'):
                                    with tag('img', src=getResultImage(x86rhel7_detail['result']),align='top',style="width: 16px; height: 16px;"):
                                        text()
                                    if x86rhel7_detail['result'] != "SUCCESS" and x86rhel7_detail['result'] != "ABORTED":
                                        text(str(x86rhel7_detail['failedCount']) + " (" + str(x86rhel7_detail['unique']) + ")")

  
result = doc.getvalue()
print "Writing result to a file at /var/www/html/ci_report.html"
with open('/var/www/html/index.html','w') as afile :
    afile.write(result.encode('utf-8'))
    
with open('/var/www/html/ci_report.html','w') as afile :
    afile.write(result.encode('utf-8'))

print 'The script took {0}'.format(datetime.now() - startTime)

