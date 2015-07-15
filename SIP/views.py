from django.shortcuts import render_to_response, render, redirect
from django.http import HttpResponseRedirect, HttpResponse
from django.core.context_processors import csrf
from django.core.mail import send_mail
from datetime import date,timedelta
from django.db import transaction
from django.contrib import auth
from django.template import Context
##ketaki
#from django.contrib.auth.decorators import login_required
#from django.contrib.auth import logout
from django.views.decorators.csrf import csrf_protect
from django.template import RequestContext
from django.contrib.auth.models import User
from SIP.models import Userlogin
from SIP.validations import retrieve_error_message,validate_login,validate_email,password_reset
from django.core.mail import send_mail
from django.contrib.auth.hashers import make_password, check_password
from django.views.decorators.cache import cache_control
from django.core.cache import cache

#importing the PersonInformation Class from models.py
from .models import *


#importing the validations from validations.py
from .validations import *
############## student management:import statements ##########################

from django.template.loader import get_template

from forms import UploadForms

from django.contrib import messages
from django.conf import settings

from django.utils.datastructures import MultiValueDictKeyError
from django.conf.urls.static import static
from django.db.models import Q
import glob 
from django.core.files import File
from SIP.models import *
import csv
import MySQLdb


#------------------------------------------
from SIP.validations import *
#------------------------------------------
#------------------------------------------
# Create your views here.

# Create your views here.

from django.utils import timezone
from django.conf import settings
from forms import UploadForms
from django.utils import timezone
from django.contrib import messages
import glob 
from django.core.files import File
from django.utils.datastructures import MultiValueDictKeyError
#from easygui import *
import csv
from bs4 import *
from urllib2 import urlopen
import sys
import cStringIO as StringIO
from django.template.loader import get_template
from django.template import Context
from cgi import escape
import urllib2,cookielib
from django.db import connection, transaction
import json
from globalss import *
from IITBOMBAYX_PARTNERS.settings import *
#############################end of import statements by student management#######################################
current=timezone.now
default_password="Welcome123"





@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def get_multi_roles(request):    
    args={}
    try:
       person=Personinformation.objects.get(email=request.session['email_id'])
    except:
          args['message'] ="unique person for logged in  user does not exit"
          return render(request,'geterror.html',args)
    

    if request.POST:        
        
        institute_id = request.POST.get('institute_id')
        #print request.POST.get('institute_id')
        request.session['institute_id']=request.POST.get('institute_id')#institute id set
        rolelist,args= roleselect(request,institute_id,person,args)
        '''rolelist=[]
        
        obj = Institutelevelusers.objects.filter(instituteid=institute_id).filter(personid=request.session['person_id']).values("roleid").distinct()
        for row in obj:
            obj=Lookup.objects.get(category='role', code=row['roleid'])
            
            rolelist.append([obj.comment,row['roleid'],0])

        cobj = Courselevelusers.objects.filter(instituteid__instituteid=institute_id).filter(personid=request.session['person_id'])
        for row in cobj:
            obj=Lookup.objects.get(category='role', code=row.roleid)
           # print row.courseid.id,row.roleid,obj.comment
            rolelist.append([obj.comment,row.roleid,row.courseid])       
        
        args={'flag':False,'rolelist':rolelist}  
        args['firstname']=person.firstname
        args['lastname']=person.lastname
        args['institutename']=T10KT_Institute.objects.get(instituteid=request.session['institute_id']).institutename
        args['email']=request.session['email_id']  
        '''
        if len(rolelist)==1:
            return onerole(request,rolelist,args)
        args.update(csrf(request)) 
        return render(request,'rolepage1.html',args)
           
                 
    l=[]  
    #person_obj = Personinformation.objects.get(email=request.session['email_id'])
    request.session['person_id']=person.id#person id set
    
   
    insti_obj=Institutelevelusers.objects.filter(personid=person.id).values("instituteid").distinct()
    
    
    for i in insti_obj:
        
        insti_x=T10KT_Institute.objects.filter(instituteid=i["instituteid"])
        x= insti_x[0].institutename
        l.append([i["instituteid"],x])
#---------------------------------------update-------------------------------------------------------------------
    insti_obj=Courselevelusers.objects.filter(personid=person.id).values("instituteid").distinct()
    
    for i in insti_obj:
        flag=True
        insti_x=T10KT_Institute.objects.filter(instituteid=i["instituteid"])
        x= insti_x[0].institutename
        for row in l:
                if row[0]==i["instituteid"]:
                        flag=False
        if flag:
                l.append([i["instituteid"],x])
  
    if len(l)==1:
       return oneinstitute(request,person)
    
        
#---------------------------------------update-------------------------------------------------------------------
    try:
       request.session['rcid']=T10KT_Approvedinstitute.objects.get(instituteid__instituteid=institute_id).remotecenterid.remotecenterid
    except:
       request.session['rcid']="   " 
    args={"l":l,'flag':True}
    args['firstname']=person.firstname
    args['lastname']=person.lastname
    args['email']=request.session['email_id'] 
    args['rcid']=request.session['rcid'] 
    args.update(csrf(request))
    
    return render(request,'rolepage1.html',args)    
        

#-----------------------------------------------------------------
def roleselect(request,institute_id,person,args):
        rolelist=[]
        obj = Institutelevelusers.objects.filter(instituteid=institute_id).filter(personid=request.session['person_id']).values("roleid").distinct()
        for row in obj:
            obj=Lookup.objects.get(category='role', code=row['roleid'])
            
            rolelist.append([obj.comment,row['roleid'],0])

        cobj = Courselevelusers.objects.filter(instituteid__instituteid=institute_id).filter(personid=request.session['person_id'])
        for row in cobj:
            obj=Lookup.objects.get(category='role', code=row.roleid)
           # print row.courseid.id,row.roleid,obj.comment
            rolelist.append([obj.comment,row.roleid,row.courseid])       
        
        args['flag']=False
        args['rolelist']=rolelist  
        args['firstname']=person.firstname
        args['lastname']=person.lastname
        args['institutename']=T10KT_Institute.objects.get(instituteid=request.session['institute_id']).institutename
        args['email']=request.session['email_id']
        
        return rolelist,args



def oneinstitute(request,person):
    args={}
    if Institutelevelusers.objects.filter(personid=person.id).exists():
        institute_id=Institutelevelusers.objects.filter(personid=person.id)[0].instituteid.instituteid
    else:
        institute_id=Courselevelusers.objects.filter(personid=person.id)[0].instituteid.instituteid
    request.session['institute_id']=institute_id#institute id set
    try:
       request.session['rcid']=T10KT_Approvedinstitute.objects.get(instituteid__instituteid=institute_id).remotecenterid.remotecenterid
    
    except:
       request.session['rcid']="   "   
    #insti_x=T10KT_Institute.objects.filter(instituteid=institute_id)
    #x= insti_x[0].institutename
    args['rcid']=request.session['rcid']
    
    rolelist,args=roleselect(request,institute_id,person,args)
    '''
    rolelist=[]
    obj = Institutelevelusers.objects.filter(instituteid=institute_id).filter(personid=request.session['person_id']).values("roleid").distinct()
    for row in obj:
            obj=Lookup.objects.get(category='role', code=row['roleid'])
            
            rolelist.append([obj.comment,row['roleid'],0])
    cobj = Courselevelusers.objects.filter(instituteid__instituteid=institute_id).filter(personid=request.session['person_id'])
    for row in cobj:
        obj=Lookup.objects.get(category='role', code=row.roleid)
           # print row.courseid.id,row.roleid,obj.comment
        rolelist.append([obj.comment,row.roleid,row.courseid])       
      
    args={'flag':False,'rolelist':rolelist}  
    args['firstname']=person.firstname
    args['lastname']=person.lastname
    args['institutename']=T10KT_Institute.objects.get(instituteid=request.session['institute_id']).institutename
    args['email']=request.session['email_id']  
    '''  
    print args     
    if len(rolelist)==1:
            return onerole(request,rolelist,args)
    args.update(csrf(request)) 
    return render(request,'rolepage1.html',args)


def onerole(request,rolelist,args):
    if rolelist[0][2]:
       args.update(csrf(request))
                    # print "role list",rolelist[0][2]
       return set_single_role(request,rolelist[0][1],rolelist[0][2].courseid,rolelist[0][2].id)        
    args.update(csrf(request))
    return set_single_role(request,rolelist[0][1],0,0)
    
    
        
   


def set_single_role(request,role,courseid,cid):
         
        request.session['role_id']=int(role)
        request.session['rolename']=Lookup.objects.get(category="Role",code=role).comment
        request.session['courseid']=courseid#role id set
        request.session['edxcourseid']=cid#role id set
        args=sessiondata(request)
        #print "sessiondata" ,args
        

        return ccourse(request)
#------------------- end of multiple role page code--------------current--


#------------------- end of multiple role page code----------------
#create dictionary with default data of session institutename,firstname,lastname,email,role_id,rolename,rcid,courseid,edxcourseid
def sessiondata(request):
    args = {}
    args.update(csrf(request))
    try:
       person=Personinformation.objects.get(email=request.session['email_id'])
       args['institute']=institute=T10KT_Institute.objects.get(instituteid=request.session['institute_id'])
       args['person']=person
    except:
          args['message'] ="Cannot fetch unique person or institute for this logged-in session "
          return render(request,'geterror.html',args)
    
    args['institutename']=institute.institutename
    args['firstname']=person.firstname
    args['lastname']=person.lastname
    args['email']=request.session['email_id']
    args['role_id']=int(request.session['role_id'])
    args['rolename']=request.session['rolename']
    args['rcid']=request.session['rcid']  
    args['courseid']= request.session['courseid']
    args['edxcourseid']=request.session['edxcourseid']
    return args             




@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def sessionlogin(request):
            
    args = {}
    args.update(csrf(request)) 
    try:
            if request.session['email_id']:
               
               user = User.objects.get(email=request.session['email_id'])
               user_info=Userlogin.objects.get(user=user)
               
               if user_info.usertypeid==0:
                   
                   return HttpResponseRedirect("/blendedadmin/")
               else:
                   return HttpResponseRedirect("/get_multi_roles/")
            else:               
                return loginn(request)
    except:
                    
            return loginn(request)


#------------------------------------------------------------------------
############## Login by Ketaki###################################
# #  Login Page Request # #
##  Author Ketaki                  Date:26-Jun-2015 ##
##  This module takes email and password as input, validates in userlogin and
##  If valid details, updates userlogin table. It also sets session variables
##  If not valid, displays error message and takes you back to the login page

@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def loginn(request):
    
    page = 'Login'
    module = 'Login'
    args = {}
    args.update(csrf(request))
    if request.method == 'POST':
        args['email']= request.POST['email']
        args['error_message']=[]
        args = emailid_validate(request,args)
        if args['error_message']:
            return render_to_response('login/tologin.html',args)            
        loginlist = validate_login(request) 
## If the emailid exists, then call the page according to the role
        if (loginlist==1):      
            return HttpResponseRedirect("/get_multi_roles/")
## If the emailid does not exist,display error message
        elif (loginlist == 0):
             return HttpResponseRedirect("/blendedadmin/")
        elif (loginlist == 2):
             return HttpResponseRedirect("/bmchome")
        elif (loginlist == 3):
             return HttpResponseRedirect("/courseadminhome/")
        else:
            error_message=retrieve_error_message(module,page,'LN_INV')
            args = {}
            args.update(csrf(request))
            args['error_message']=error_message
            return render_to_response('login/tologin.html',args)            
    return render_to_response('login/tologin.html',args)
           
           





#############################################multiple role########################################################


######################## Registration  #####################################


def emailto_higherauthorities(reqid):
    rcobj = RequestedUsers.objects.filter(id=reqid)
    print rcobj,"asfdsdf"
    rcobj1=rcobj[0]
    print rcobj1,"ssdf"

    #fetch institute id and roleid
    insid=rcobj1.instituteid.instituteid
    print insid
    roleid=rcobj1.roleid
    courseid = rcobj1.roleid
    
    #fetch all authorities above this person and send them email regarding request 
    inslevelobj=Institutelevelusers.objects.filter(instituteid=insid)
    if inslevelobj : #only if we request.session['courseid'get any object proceed
        for row in inslevelobj:
            if row.roleid < roleid :# take only higher authorities and send them a mail
                print row.personid.id,"123",type(row.personid.id)
                send_email(2,reqid,row.personid.id)
    
    if roleid <= 5: # only if user is teacher fetch all coure-co-od's from this table 
        courselevelobj=Courselevelusers.objects.filter(instituteid=insid,courseid=courseid)    
        for row in courselevelobj:
            if row.roleid < roleid and row.courseid == courseid  :# to respective course course-co-od 
                send_email(2,reqid,row.personid)
   
    return 1 
   
   
def forgot_pass(request):
    module = 'Login'
    page = 'Forgot_Pass'
    args = {}
    args.update(csrf(request))
    if request.method == 'POST':        
        email = request.POST['email']
        per_id= validate_email(email)
## If valid email id, then a mail is sent to his email alongwith a link to reset his password 
        if per_id != -1:     
            args['message']= retrieve_error_message(module,page,'NO_ERR')
            try:
               ec_id = EmailContent.objects.get(systype='Login', name='resetpass').id
            except:
               args['message'] ="Email cannot send at this moment. "
               return render(request,'geterror.html',args)
           #print ec_id
            send_email(ec_id, per_id, per_id)
            return render_to_response('login/forgot_pass.html',args)                
        else:
## If invalid email, displays an error message
            args['message']=retrieve_error_message(module,page,'EML_INV')
            return render_to_response('login/forgot_pass.html',args)        
    return render_to_response('login/forgot_pass.html',args)
 
def resetpass(request,emailid):
    per_id = emailid
    module = 'Login'
    page = 'Reset_Pass'
    args = {}
    args.update(csrf(request))   
    if request.method == 'POST':

        args['password1']= password1=request.POST.get('new_password1','')
        args['password2']= password2=request.POST.get('new_password2','')
        args['message']=[]
        args = pwd_field_empty(request,args,'')
        if args['message']:
            return render_to_response('login/resetpass.html',args)

        if  len(password1)==0 or len(password2)==0 or password1 != password2:

            args['message']= retrieve_error_message(module,page,'NO_MTCH')
            return render_to_response('login/resetpass.html',args)
        else:
## If the two new passwords match, password is changed and a mail is sent to the user regarding the change
            try: 
                userid=Personinformation.objects.get(id=emailid)           
                user = User.objects.get(email=userid.email)
            except:
               args['message'] ="unique person for the user does not exist"
               return render(request,'geterror.html',args)
            user.set_password(password1)
            user.save()
            args['message']= retrieve_error_message(module,page,'PWD_SET')
            ec_id = EmailContent.objects.get(systype='Login', name='success').id
            send_email(ec_id, per_id, per_id)
            return render_to_response('login/change_pwdsuccess.html',args)            
  
    return render_to_response('login/resetpass.html',args)

#############createpassword########################
def createpass(request,emailid):
    per_id = emailid
    module = 'Login'
    page = 'Reset_Pass'
    args = {}
    args.update(csrf(request))
    try:
       userid=Personinformation.objects.get(id=emailid)
   
       if Userlogin.objects.get(user=User.objects.get(email=userid.email)).status==0:   
		  if request.method == 'POST':

		     args['password1']=password1= request.POST.get('new_password1','')
		     args['password2']=password2= request.POST.get('new_password2','')
		     args['message']=[]
		     args = pwd_field_empty(request,args,'')
		     if args['message']:
		        return render_to_response('login/createpass.html',args)

		     if  len(password1)==0 or len(password2)==0 or password1 != password2:
		        args['message']= retrieve_error_message(module,page,'NO_MTCH')
		        return render_to_response('login/createpass.html',args)

		     else:  
	  ## If the two new passwords match, password is changed and a mail is sent to the user regarding the change 
		                 
		        userid=Personinformation.objects.get(id=emailid)           
		        user = User.objects.get(email=userid.email)           
		        user.set_password(password1)
		        user.save()
		        user_info=Userlogin.objects.get(user=user)
		        user_info.status=1
		        user_info.save()
		        args['message']= retrieve_error_message(module,page,'PWD_SET')
		        ec_id = EmailContent.objects.get(systype='Login', name='success').id
		        send_email(ec_id, per_id, per_id)
		        return render_to_response('login/create_pwdsuccess.html',args)            
	  
		  #return render_to_response('login/createpass.html',args)
       return  render_to_response('login/alreadycreated.html',args)

    except:
           args['message'] ="person  does not exist"
           return render(request,'geterror.html',args)

###################################################



'''

def selectcourse(request):

      scourse = request.GET['id']
      print scourse
      cl=[]time
      apinid=T10KT_Institute.objects.get(institutename=scourse).instituteid
      print apinid
     # encourseid = courseenrollment.objects.filter(instituteid__instituteid__instituteid=apinid)
      encourseid = courseenrollment.objects.filter(instituteid__instituteid__instituteid=apinid)
      for i in encourseid:
         #  print i.courseid.course
           cl.append([i.courseid.course,i.courseid.id])

      list1 = edxcourses.objects.raw("SELECT DISTINCT SIP_edxcourses.course, SIP_edxcourses.coursename, SIP_edxcourses.id FROM SIP_edxcourses, SIP_courseenrollment, SIP_t10kt_approvedinstitute WHERE SIP_edxcourses.courseid = SIP_courseenrollment.courseid_id and SIP_courseenrollment.instituteid_id ='%d'"%(apinid))


      print list1
      data = serializers.serialize('json',list1 )
      return HttpResponse(json.dumps(data), content_type="application/json")

###########################################################################################################

######################################## End of Registration ###########################################################

########################### Student management code ###################################################
'''#Function to show the teacher list of a particular course and institute.

@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def logout(request):
    logout_obj = User.objects.get(email=request.session['email_id'])
   # logout_obj.loginstatus='False'
    logout_obj.save()
    try:
		del request.session['person_id']
		del request.session['email_id']
		del request.session['institute_id']
		request.session.flush()
		cache.clear()
		auth.logout(request)
		#return HttpResponseRedirect('/')
		response = HttpResponseRedirect('/')
		response['Cache-Control'] = 'no-cache, no-store, max-age=0, must-revalidate'
		response.delete_cookie()
		return response
   
    except:
        return HttpResponseRedirect('/')





def ccourse(request):
    # args contain  default data of session with  these parameter institutename,firstname,lastname,email,role_id,rolename,rcid,courseid,edxcourseid ,institute instance and person instance and use args to add your  data and send  in html 
    args =sessiondata(request)
    input_list={}
    
    input_list.update(args)
	#input_list['rolename']=request.session['rolename']
    input_list.update(csrf(request))
    #input_list['email']=request.session['email_id']
   
    #viewer_obj=Personinformation.objects.get(id = request.session['person_id'])
    #print args['role_id'] ,"aiur ye kar ke dikhao",request.session['role_id']
    input_list['roleid']=args['role_id']
        
    if input_list['roleid']==4:
		return HttpResponse('/coordinatorhome/')
    if input_list['roleid']==5:
		
		return HttpResponseRedirect('/teacher/')
    input_list['viewer'] = args['person'].id

    enrolled_courses=courseenrollment.objects.filter(status=1, instituteid__instituteid=request.session['institute_id'])

    edx_enrolled_courses=[]
    try:
       for index in enrolled_courses:
		  edx_enrolled_courses.append(edxcourses.objects.get(courseid=index.courseid.courseid))
    except:
           args['message'] ="cannot get unique entry for course"
           return render(request,'geterror.html',args)

    input_list['courselist'] = edx_enrolled_courses
    #person=Personinformation.objects.get(email=request.session['email_id'])
	#input_list['firstname']=person.firstname
	#input_list['lastname']=person.lastname
    input_list['cid']=args['edxcourseid']
	#input_list['rcid']=request.session['rcid']
	#input_list['institutename']=T10KT_Institute.objects.get(instituteid=request.session['institute_id']).institutename
    return render(request,enrolled_course_, input_list)




#---------------------------------------#'''

#Function to show the teacher list of a particular course and institute.

def teacherlist(request,courseid):
        # args contain  default data of session with  these parameter institutename,firstname,lastname,email,role_id,rolename,rcid,courseid,edxcourseid ,institute instance and person instance and use args to add your  data and send  in html 
        args =sessiondata(request)
        args.update(csrf(request))
        #person=Personinformation.objects.get(email=request.session['email_id'])
        #args['institutename']=T10KT_Institute.objects.get(instituteid=request.session['institute_id']).institutename
        #args['coursename']=edxcourses.objects.get(courseid=courseid).course
        #args['firstname']=person.firstname
        #args['lastname']=person.lastname
        #args['email']=request.session['email_id']
        #args['role_id']=int(request.session['role_id'])
        #args['rolename']=request.session['rolename']
        #args['rcid']=request.session['rcid']
        #course = id of a particular course corresponds to edx courses
        teacherlist = []    #list to append teacher's name
        #collect all objects from courselevelusers of a particular institute and course   
             
        users = Courselevelusers.objects.filter(instituteid__instituteid = request.session['institute_id'],roleid = 5).filter(courseid__courseid = courseid)
        for user in users: #iterate over all objects
                teacherlist.append(user)   #append first name to the list
                args['coursename'] = user.courseid.coursename
        #Context = {'list' :  list,'courseid':courseid}   #make a context to display on html
        args['teacherlist'] = teacherlist
        args['courseid'] = courseid
       
        return render_to_response("student/teacher.html",args, context_instance=RequestContext(request))

#---------------------------------------#
#Function to show all the courses taken by a institute

def courselist(request):
    #args = {}
    # args contain  default data of session with  these parameter institutename,firstname,lastname,email,role_id,rolename,rcid,courseid,edxcourseid ,institute instance and person instance and use args to add your  data and send  in html 
    args =sessiondata(request) 
    args.update(csrf(request))
    #person=Personinformation.objects.get(email=request.session['email_id'])
    #args['firstname']=person.firstname
    #args['lastname']=person.lastname
    #args['email']=request.session['email_id']
    #args['role_id']=request.session['role_id']
    #args['institutename']=T10KT_Institute.objects.get(instituteid=request.session['institute_id']).institutename
    #args['rcid']=request.session['rcid']
    #find all the objects of a courselevelusers where personid matches with login id
    obj = Courselevelusers.objects.filter(personid_id = request.session['person_id'],courseid__courseid = request.session['courseid'],instituteid__instituteid=request.session['institute_id'],roleid = request.session['role_id'])
    #print obj
    #Context = {'courses' : obj}   #make a context of all objects
    args['courses'] = obj
    for i in obj:
        args['coursename'] = i.courseid.coursename        
    return render_to_response("student/coordinator_firstPage.html",args,context_instance=RequestContext(request))

    
#------------------------------------#
'''
#Function to show all the courses taken by a institute

def courselist(request):
    args = {}
    args.update(csrf(request))
    person=Personinformation.objects.get(email=request.session['email_id'])
    args['firstname']=person.firstname
    args['lastname']=person.lastname
    args['email']=request.session['email_id']
    args['role_id']=request.session['role_id']
    args['institutename']=T10KT_Institute.objects.get(instituteid=request.session['institute_id']).institutename
    a=[]
    courselevel=Courselevelusers.objects.filter(personid__id=request.session['person_id'])
    print courselevel[0].courseid.id
    if courselevel:
            ecourses=edxcourses.objects.filter(id=courselevel[0].courseid.id)
            print ecourses
    for course in ecourses:
        print course.coursename
        a.append(course.coursename)
   
    args['courses_list'] = a
 
    return render_to_response("student/courses.html",args,context_instance=RequestContext(request))'''
    
#------------------------------------#
  
#Function to display details all student for a particular institute, teacher and course

def studentdetails(request,courseid,pid):
    # args contain  default data of session with  these parameter institutename,firstname,lastname,email,role_id,rolename,rcid,courseid,edxcourseid ,institute instance and person instance and use args to add your  data and send  in html 
    args =sessiondata(request)
    #args = {}
    args.update(csrf(request))
    #person=Personinformation.objects.get(email=request.session['email_id'])
    #args['firstname']=person.firstname
    #args['lastname']=person.lastname
    #args['email']=request.session['email_id']
    #args['institutename']=T10KT_Institute.objects.get(instituteid=request.session['institute_id']).institutename
    #print course
    try:
       courseobj = edxcourses.objects.get(courseid = courseid)
       args['coursename']=courseobj.coursename
    except:
           args['message'] ="cannot get entry for course"
           return render(request,'geterror.html',args)
    #args['role_id']=request.session['role_id']
    args['personid']=request.session['person_id']
    #args['rolename']=request.session['rolename']
    #args['rcid']=request.session['rcid']
    try:
        courselevelid=Courselevelusers.objects.get(personid__id=pid,courseid__courseid=courseid,startdate__lte=current,enddate__gte=current)
    except:
           args['message'] ="You are not valid Teacher for this course"
           return render(request,'geterror.html',args)
    students = studentDetails.objects.filter(teacherid__id=courselevelid.id,courseid=courseid)#select all students who belong to this teacher and course
    data=[]    #list to append data
    for student in students:   #iterate over objects of studentdetails
		try:

			data.append([student.edxuserid.pk,student.roll_no,student.edxuserid.username,student.edxuserid.email])
		except :
				continue
                
    data.sort()   #sort to print data in sorted order
 
    args['info']=data
    args['courseid']=courseid
    args['id'] = pid
    return render_to_response("student/studentdetails.html",args,RequestContext(request))

#-----------------------------------------#

#-----------------------------------------#

#Function to parse the sql query and return all the data in a list

def sql_select(sql):
    cursor = connection.cursor()
    cursor.execute(sql)
    results = cursor.fetchall()
    list = []
    i = 0
    for row in results:
        dict = {} 
        field = 0
        while True:
           try:
                dict[cursor.description[field][0]] = str(results[i][field])
                field = field +1
           except IndexError as e:
                break
        i = i + 1
        list.append(dict) 
    return list  

#-------------------------------------------#

def downloadcsv(request,course,id):
    personid = 0
    if int(id) == 0:
        personid = request.session['person_id']
    else:
        personid = int(id)
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="student_details"'+str(personid)+'.csv'
    context=RequestContext(request)
    writer = csv.writer(response)
    writer.writerow(["Roll_No", "Username","Email-ID"])
    csvdata = studentDetails.objects.filter(teacherid_id = personid,courseid__courseid = course)
    for row in csvdata:
        writer.writerow([row.roll_no,row.userid.username,row.userid.email])
    return response

'''
#Function to parse the html and make a download file in csv format

def downloadcsv(request,course):
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="student_details.csv"'
    context=RequestContext(request)
    print "hwsafc"
    soup = BeautifulSoup(urlopen('http://10.105.22.21:9005/parse/'+course))
    print course
    division = soup.findAll('div',{ "class" : None })
    for d in division:
        table = d.findAll('table')
        for t in table:
            headers =[]
            headers.append([header.text.encode('utf8') for header in t.findAll('th')])
            rows = []
            for row in t.findAll('tr'):
                rows.append([val.text.encode('utf8') for val in row.findAll('td')])
                with open('student_details.csv', 'w') as f:
                    writer = csv.writer(f)
                    writer.writerows(headers)
                    writer.writerows(row for row in rows if row)
        writer = csv.writer(response)
        with open('/home/tushar/Desktop/student_details.csv', 'rb') as csvfile:#update path to save csv file
            filereader = csv.reader(csvfile, delimiter=',')
            for row in filereader:
                writer.writerow(row)
        return response

    return HttpResponse('')
    #return response

'''
#---------------------------------#

#Function to provide facility to update roll_no of student

def Update(request,pid,courseid,t_id):
    # args contain  default data of session with  these parameter institutename,firstname,lastname,email,role_id,rolename,rcid,courseid,edxcourseid ,institute instance and person instance and use args to add your  data and send  in html 
    args =sessiondata(request)
    #args = {}
    args.update(csrf(request))
    #person=Personinformation.objects.get(email=request.session['email_id'])
    #args['institutename']=T10KT_Institute.objects.get(instituteid=request.session['institute_id']).institutename
    args['coursename']=edxcourses.objects.get(courseid=courseid).course
    #args['firstname']=person.firstname
    #args['lastname']=person.lastname
    #args['email']=request.session['email_id']
    #args['role_id']=int(request.session['role_id'])
    #args['rolename']=request.session['rolename']
    #args['rcid']=request.session['rcid']    

    #pid = id of selected student related to auth_user table
    if request.method == 'POST':
        #update student roll_no with textbox value
        studentDetails.objects.filter(edxuserid__username = request.POST['username']).update(roll_no = request.POST['roll_no'])
        #student = studentDetails.objects.get(edxuserid__edxuserid = pid)
        #userid = student.edxuserid_id
        user = iitbx_auth_user.objects.get(edxuserid = pid)
        #firstname = user.firstname
        #email = user.email
        #print t_id,type(t_id),"dsd",request.session['courseid']
        #teacherid = 0        
        #if int(t_id) == 0:
         #       teacherid = request.session['person_id']
        #else:
         #       teacherid = request.session['person_id']
       # teacher = Personinformation.objects.get(id = t_id)
		#teacher = Personinformation.objects.get(id = teacherid)
        #teachername = teacher.firstname
        #teachername += (" "+teacher.lastname)
        #teacheremail = teacher.email
        #newroll = request.POST['roll_no']
        return HttpResponseRedirect('/studentdetails/'+courseid+'/'+t_id)
		#return HttpResponseRedirect('/studentdetails/'+request.session['courseid']+'/'+t_id)
    else:
        
        #get the student object of given id
        student = studentDetails.objects.get(edxuserid__edxuserid=pid)
        args = {}
        args.update(csrf(request))
        args['info']=student
        args['courseid']=courseid
        args['pid']=pid
        args['t_id'] = t_id
        return render_to_response("student/update.html",args)

#---------------------------------# 
'''
#Function to provide facility to update roll_no of student

def Update(request,pid,course,t_id):
    #pid = id of selected student related to auth_user table
    if request.method == 'POST':
        #update student roll_no with textbox value
        studentDetails.objects.filter(userid__username = request.POST['username']).update(roll_no = request.POST['roll_no'])
        
        #redirect to studentdetails page
        return HttpResponseRedirect('/studentdetails/'+"IITBombayX/"+course+"/2015-16/"+t_id)
    else:
        
        #get the student object of given id
        student = studentDetails.objects.get(id=pid)
        args = {}
        args.update(csrf(request))
        args['info']=student
        args['course']=course
        args['pid']=pid
        args['t_id'] = t_id
        return render_to_response("student/update.html",args)

#---------------------------------# 
         

#Function to provide facility to change roll_no of student

def Update(request,pid,course):
    print course
    
    #args = {}
    #args.update(csrf(request))
    if request.method == 'POST':
        
        studentDetails.objects.filter(userid__username = request.POST['username']).update(roll_no = request.POST['roll_no'])
        return HttpResponseRedirect('/parse/'+'IITBombayX/'+course+"/2015-16")
    else:
        
        student = studentDetails.objects.get(id=pid)
        args = {}
        args.update(csrf(request))
        args['info']=student
        args['course']=course
        args['pid']=pid
        args['a']=pid
        return render_to_response("student/update.html",args)'''
    

#---------------------------------# 
         

#Function for bulk move of students from one teacher to another  (For higher authority accept teacher)
def movestudents(request):
    args = {}
    args.update(csrf(request))
    form = UploadForms()
    args['form'] = formlist1
    teacherlist = Courselevelusers.objects.filter(instituteid = request.session['institute_id']).filter(roleid = 5)#give one more filter for course
    args['info'] = teacherlist
   
    return render_to_response('student/bulkremovefirstpage.html',args)

#-------------------------------------#

        
#-------------------------------------------#
#this function is used to output a csv file #
#-------------------------------------------#
#-------------------------------------------#
     
'''
def upload(request,code):
    args = {}
    args.update(csrf(request))
    person=Personinformation.objects.get(email=request.session['email_id'])
    args['firstname']=person.firstname
    args['lastname']=person.lastname
    args['email']=request.session['email_id']
    args['institutename']=T10KT_Institute.objects.get(instituteid=request.session['institute_id']).institutename
    args['role_id']=request.session['role_id']
    personid=request.session['person_id']
    course=Courselevelusers.objects.get(personid=request.session['person_id']).courseid.courseid
    coursename=edxcourses.objects.get(courseid=course).coursename
    args['coursename']=coursename
    if request.POST:
        form = UploadForms(request.POST, request.FILES)
        if form.is_valid():
            a = form.save()
            for p in uploadedfiles.objects.raw('SELECT * FROM SIP_uploadedfiles where uploadedby_id = 1 ORDER BY id DESC LIMIT 1 '):
                #print "file"
                fname = str(p.filename)
            uploadedfiles.objects.filter(filename = fname).update(uploadedby = request.session['person_id'])        
            extension = validate_file_extension(fname)
            if(extension):
                #print request.POST['teacher_id']
                if int(request.session['role_id'])==4:
                    context = parse(request,False,request.POST['teacher_id'],fname)     # 'parse' function is defined in validations.py
                    return render(request, 'student/uploaded.html', context)
                elif int(request.session['role_id'])==5:
                    personid=request.session['person_id']
                    course=Courselevelusers.objects.get(personid=request.session['person_id']).courseid.courseid
                    coursename=edxcourses.objects.get(courseid=course).coursename
                    firstname=Personinformation.objects.get(id=personid).firstname
                    lastname=Personinformation.objects.get(id=personid).lastname
                    teachername = firstname+lastname
                    context = parse(request,True,False,fname)     # 'parse' function is defined in validations.py 
                    context['teachername']=teachername
                    context['coursename']=coursename               
                    return render(request, 'student/uploaded.html', context)
            else:
                
                message = " !!! Please Upload .csv File!!!"
                form = UploadForms()
                
    
                args['form'] = form
                args['message'] = message
                return render_to_response('student/upload.html', args)
           
    else:
        form = UploadForms()
        
    
    
    args['form'] = form
    
    return render_to_response('student/upload.html', args)'''
        
#---------------------------------------------------------

#-------------------------------------------#
#this function is used to output a csv file #
#-------------------------------------------#
#-------------------------------------------#
def upload(request,code,courseid):

   # args contain  default data of session with  these parameter institutename,firstname,lastname,email,role_id,rolename,rcid,courseid,edxcourseid and use args to add your  data and send  in html 
   args =sessiondata(request)

   args.update(csrf(request))
   person=Personinformation.objects.get(email=request.session['email_id'])
   #args['institutename']=T10KT_Institute.objects.get(instituteid=request.session['institute_id']).institutename
   args['coursename']=edxcourses.objects.get(courseid=courseid).course
  
    
   if request.POST:
        form = UploadForms(request.POST, request.FILES)
        teacher_id = request.session['person_id'] 
        fname=request.FILES['filename'].name        
        if form.is_valid():
           
            a = form.save()
            for p in uploadedfiles.objects.raw('SELECT * FROM SIP_uploadedfiles where uploadedby_id = 1 ORDER BY id DESC LIMIT 1 '):
                    changedfname = str(p.filename)
            
            uploadedfiles.objects.filter(filename = fname).update(uploadedby = teacher_id)
            extension = validate_file_extension(fname)
            if(extension):
                if code == "2":
                    #print "upload view code 2 calling validatefileinfo"
                    context = validatefileinfo(request,courseid,changedfname,teacher_id)
                    #context = parse(request,courseid,changedfname)     # 'parse' function is defined in validations.py
                    #update_students(request,context['errorreport'])
                    context.update(args)
                    return render(request, 'student/uploaded.html', context)
            else:
                message = " !!! Please Upload .csv File!!!"
                form = UploadForms()
                args = {}
                args.update(csrf(request))
    
                args['form'] = form
                args['message'] = message
                return render_to_response('student/upload.html', args)
           
   else:
        form = UploadForms()  
     
   args['form'] = form
   args['courseid']=courseid
   return render_to_response('student/upload.html', args)

def output_csv(request,code):
   
    for p in uploadedfiles.objects.raw('SELECT * FROM SIP_uploadedfiles ORDER BY id DESC LIMIT 1 '):
        fname = str(p.filename)    
    personid = request.session['person_id']
   
    timestr = datetime.now().strftime("%d-%m-%Y_%H:%M:%S")
    # Create the HttpResponse object with the appropriate CSV header.
    response = HttpResponse(content_type='text/csv')
    courseid=request.session['courseid']
#---------------------
    if(code=="1"):
        downloadfile = "%s_%s_%s_%s" % ("report","valid",courseid,timestr)#1
        downloadfile=downloadfile+".csv"
        response['Content-Disposition'] = 'attachment; filename="%s"'%(downloadfile)
        
        #print filename
        writer = csv.writer(response)
        #csvdata = student_interface.objects.filter(errorcode__errorcode = "noerror",fileid__filename = fname) 
        csvdata = student_interface.objects.filter(error_message = "SUCCESS",fileid__filename = fname) 
        #csvdata = Errorincsv.objects.all()        
        writer.writerow(["Record No","Roll No", "Username","Email-ID"])
        for row in csvdata:
            writer.writerow([row.recordno,row.roll_no, row.username, row.email])
#---------------------
    elif(code=="2"):
        downloadfile = "%s_%s_%s_%s" % ("report","invalid",courseid,timestr)#1
        downloadfile=downloadfile+".csv"
        response['Content-Disposition'] = 'attachment; filename="%s"'%(downloadfile)
        print code
        #print filename
        writer = csv.writer(response)
        csvdata = student_interface.objects.filter(~Q(error_message = "SUCCESS"),fileid__filename = fname)  
        #csvdata = Errorincsv.objects.all()        
        writer.writerow(["Record No","Roll No", "Username","Email-ID","Message"])
        for row in csvdata:
            writer.writerow([row.recordno,row.roll_no, row.username, row.email,row.error_message])
        

    return response
           
            

#-------------------------------------------#
#-------------------------------------------#
#-----------------------------------------------------#
#this function updates student details
#-----------------------------------------------------#

def update_students(request,errorreport):
        print request.session['person_id']
        for row in errorreport:
                if row.errorcode.errorcode=="noerror":
                        
                        studentDetails.objects.filter(userid__username = row.username).update(roll_no = row.roll_no)
                        print "in if"
                studentDetails.objects.filter(userid__username = row.username).update(teacherid_id = request.session['person_id'])
         

#-----------------------------------------------------#

 
    
def uploaded(request):
    t = get_template('student/uploaded.html')
    html = t.render(Context({}))
    return HttpResponse(html)

# Functon to list all the courses of a teacher

def teacherhome(request):
     
# args contain  default data of session with  these parameter institutename,firstname,lastname,email,role_id,rolename,rcid,courseid,edxcourseid and use args to add your  data and send  in html 
    args =sessiondata(request)
    current_date=date.today()
    args.update(csrf(request))
    person=Personinformation.objects.get(email=request.session['email_id'])
    args['pid']=request.session['person_id']
    
    #print args['edxcourseid']
    #courses = edxcourses.objects.values('courseid').distinct()
    #a=[]
    #args['role_id']=request.session['role_id']
    a=[]
    #select courselevel object of the teacher who has login
    #person = Courselevelusers.objects.get(personid = request.session['person_id'],courseid=request.session['edxcourseid'],startdate__lte=current_date,enddate__gte=current_date,instituteid=request.session[)
    
    #select all the courses from edxcourses table
    course=edxcourses.objects.get(id=request.session['edxcourseid'])
    a.append(course)
    #Context = {'courses_list': a} #send the context to the html page to display the courses
    args['courses_list'] = a
    return render_to_response("student/teacherhome.html",args, context_instance=RequestContext(request))



# Function for unenrollment of a student

def unenrollstudent(request,pid,courseid,t_id):
	# args contain  default data of session with  these parameter institutename,firstname,lastname,email,role_id,rolename,rcid,courseid,edxcourseid and use args to add your  data and send  in html 
	args =sessiondata(request)
    #pid = id of student related to studentdetails 
    #courseid = id of course related to edxcourses
    #teacherid = 0
    #if int(t_id) == 0:
        #teacherid = request.session['person_id']
    #else:
        #teacherid = int(t_id)
    #updating teacherid of a student whose id matches with the argument id  
	 
	studentDetails.objects.filter(edxuserid__edxuserid = pid).filter(courseid = courseid).update(teacherid = 1)
	#studentDetails.objects.filter(id = pid).filter(courseid = courseid).update(teacherid = 1)
    #student = studentDetails.objects.get(id = pid)
    #print pid
    #userid = student.userid_id
    #print userid
    #mail_obj = EmailContent.objects.filter(systype='SM',name = "unenroll")
    #mail_obj2 = EmailContent.objects.filter(systype='SM',name = "unenrollstud")
    #user = IITBX_authuser.objects.get(id = userid)
	try:
	    user = iitbx_auth_user.objects.get(edxuserid = pid)
	except:
           args['message'] ="user is not part of IITBombayX"
           return render(request,'geterror.html',args)
    #firstname = user.firstname
    #email = user.email
    #teacher = Personinformation.objects.get(id = teacherid)
    #teachername = teacher.firstname
    #teachername += (" "+teacher.lastname)
    #course = edxcourses.objects.get(courseid = courseid)
    #coursename = course.coursename
    #teacheremail = teacher.email
    #print firstname,email,coursename
    #message = mail_obj[0].message %(firstname,teachername,coursename)
    #message2 = mail_obj2[0].message %(teachername,firstname,coursename)
    #send_mail(mail_obj[0].subject, message , EMAIL_HOST_USER ,[email], fail_silently=False)
    #send_mail(mail_obj2[0].subject, message2 , EMAIL_HOST_USER ,[teacheremail], fail_silently=False)
    #redirect to the studentdetails page with changes
	#return HttpResponseRedirect('/studentdetails/'+courseid+"/"+t_id)
	return HttpResponseRedirect('/studentdetails/'+courseid+"/"+t_id)

def substituteteacher(request):
        args = {}
        args.update(csrf(request))
        person=Personinformation.objects.get(email=request.session['email_id'])
        args['institutename']=T10KT_Institute.objects.get(instituteid=request.session['institute_id']).institutename
        course = edxcourses.objects.get(courseid = request.session['courseid'])
        args['coursename']=course.coursename
        args['firstname']=person.firstname
        args['lastname']=person.lastname
        args['email']=request.session['email_id']
        args['role_id']=int(request.session['role_id'])
        if request.method == "POST":
                source = Personinformation.objects.filter(email = request.POST['sourceemail'])
                target = Personinformation.objects.filter(email = request.POST['targetemail'])
                #print request.POST['sourceemail'],request.POST['targetemail']
                #print source,target
                list = []
                error = False
                if len(source) == 0:
                        #args['error'] = "Source teacher email does not exists!!!"
                        error = True
                        list.append(ErrorContent.objects.get(errorcode = "s_email").error_message)
                        #return render_to_response('student/substituteteacher.html',args)
                if len(target) == 0:
                        error = True
                        args['is_error'] = True
                        #args['error'] = "Target teacher email does not exists!!!"
                        list.append(ErrorContent.objects.get(errorcode = "t_email").error_message)
                if error:
                        args['is_error'] = True
                        args['errors'] = list
                        args['source'] = request.POST['sourceemail']
                        args['target'] = request.POST['targetemail']
                        return render_to_response('student/substituteteacher.html',args)
                
                
                students = studentDetails.objects.filter(teacherid_id = source[0].id)#include course from session
                list = []
                for student in students:
                        list.append(student)
                args['students'] = list
                students = studentDetails.objects.filter(teacherid_id = source[0].id).update(teacherid_id = target[0].id)#include course from session    
                
                return render_to_response('student/completepage.html',args)
        else:        
                
                return render_to_response('student/substituteteacher.html',args)

def complete(request):
        return courselist(request)


# function to provide utility of add student

def addstudent(request,pid):
        if request.method == "POST":
                args = {}
                args.update(csrf(request))
                username = request.POST['username']
                email = request.POST['email']
                roll_no = request.POST['roll_no']
                students = studentDetails.objects.all()
                students = studentDetails.objects.get(edxuserid__email=email)
                if int(pid) == 0:
                   studentDetails.objects.filter(edxuserid__username = username).update(teacherid_id   =request.session['person_id'],roll_no = roll_no)
                else:
                   studentDetails.objects.filter(edxuserid__username = username).update(teacherid_id=int(pid),roll_no = roll_no)
                teacherid = 0
                if int(pid) == 0:
                   teacherid = request.session['person_id']
                else:
                   teacherid = request.session['person_id']
                userid = student.edxuserid_id
                user = IITBX_authuser.objects.get(id = userid)
                firstname = user.firstname
                email = user.email
                teacher = Personinformation.objects.get(id = teacherid)
                teachername = teacher.firstname
                teachername += (" "+teacher.lastname)
                course = edxcourses.objects.get(courseid = student.courseid.courseid)
                coursename = course.coursename
                teacheremail = teacher.email
                return HttpResponseRedirect('/studentdetails/IITBombayX/CS101.1x/2015-16/%d')
                                        #print firstname,email,coursename
                                        #message = mail_obj[0].message %(firstname,teachername,coursename)
                                        #message2 = mail_obj2[0].message %(teachername,firstname,coursename)
                                        #send_mail(mail_obj[0].subject, message , EMAIL_HOST_USER ,[email], fail_silently=False)
                                        #send_mail(mail_obj2[0].subject, message2 , EMAIL_HOST_USER ,[teacheremail], fail_silently=F
                #print username,email
            
                args['iserror'] = True
                args['id'] = pid
                list = []
                if not user:
                        #args['error'] = "Username is invalid!!!"
                        list.append(ErrorContent.objects.get(errorcode = "inv_user").error_message)
                        
                if not emailid:
                        #args['error'] = "Email does not exist!!!"
                        list.append(ErrorContent.objects.get(errorcode = "inv_email").error_message)
                args['errors'] = list
                args['username'] = request.POST['username']
                args['email'] = request.POST['email']
                args['roll_no'] = request.POST['roll_no']
                return render_to_response('student/addstudent.html',args)
        
        args = {}
        args.update(csrf(request))
        args['id'] = pid                        
        return render_to_response('student/addstudent.html',args)
        
#..........................................#

# function to provide facility for mass unenrollment

def massunenroll(request):
        args = {}
        args.update(csrf(request))
        person=Personinformation.objects.get(email=request.session['email_id'])
        args['institutename']=T10KT_Institute.objects.get(instituteid=request.session['institute_id']).institutename
        #args['coursename']=course
        course = edxcourses.objects.get(courseid = request.session['courseid'])
        args['coursename']=course.coursename
        args['firstname']=person.firstname
        args['lastname']=person.lastname
        args['email']=request.session['email_id']
        args['role_id']=int(request.session['role_id'])
        if request.method == "POST":
                teacher = Personinformation.objects.filter(email = request.POST['email'])
                if len(teacher) == 0:
                        #args['error'] = "Email does not exist!!!"
                        args['is_error'] = True
                        args['error'] = ErrorContent.objects.get(errorcode = "inv_email").error_message
                        args['mail'] = request.POST['email']
                        return render_to_response('student/massunenrollment.html',args)
                students = studentDetails.objects.filter(teacherid_id = teacher[0].id)
                list = []
                for student in students:
                        list.append(student)
                args['students'] = list
                students = studentDetails.objects.filter(teacherid_id = teacher[0].id).update(teacherid_id = 1)
                return render_to_response('student/unenrolledstudents.html',args)
        else:
                return render_to_response('student/massunenrollment.html',args)


'''
# Function to provide facility for unenrollment

def unenrollstudent(request,pid,courseid):
    print pid,courseid
    studentDetails.objects.filter(id = pid).filter(courseid = courseid).update(teacherid = 1)
    return HttpResponseRedirect('/parse/'+courseid)'''

#..........................................#
"""
def Print(request,row):
    #print row
    db = MySQLdb.connect("localhost","root","root","SIP_DATA")
    cursor = connection.cursor()
    sql="select SIP_iitbx_authuser.username,SIP_iitbx_authuser.email,SIP_studentdetails.roll_no from SIP_iitbx_authuser,SIP_studentdetails where SIP_studentdetails.userid_id = SIP_iitbx_authuser.id and SIP_iitbx_authuser.username = '%s'"%(row)
    
    data = sql_select(sql)
    db.close()
    context = {'info':data}
    print context
    return render_to_response("student/update.html",context,RequestContext(request))
"""    
################################################## End of student management module ########################################################



#######    performance module    #######
import csv
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
#################################################################################################
#        This section is for Performance Module.                                                        #
#        It generates the performance report of students.                                        #
#################################################################################################

def report(request,option,course):
            pinfo = {}
            pinfo.update(csrf(request))
            person=Personinformation.objects.get(email=request.session['email_id'])
            '''pinfo['firstname']=person.firstname
            pinfo['lastname']=person.lastname
            pinfo['email']=request.session['email_id']
            pinfo['institutename']=T10KT_Institute.objects.get(instituteid=request.session['institute_id']).institutename
            pinfo['role_id']=request.session['role_id']
            #course=Courselevelusers.objects.get(personid=request.session['person_id']).courseid.courseid
            #course=course
            coursename=edxcourses.objects.get(courseid=course).coursename
            edxcourse=edxcourses.objects.get(courseid=course).course
            pinfo['coursename']=coursename
            #grades=getall_student_grades(course)
            # temp function to get grades from local system for testing
            grades=get_temp()
            #type
            performance_interface.objects.filter(courseid=course).delete()
            pinfo['teachername']=person.firstname+" "+person.lastname
            report_headings =[]
            #header=[]
            #data=[]
            report_details =[] 
            i=0
            report_headings.append(grades[0])
            report_headings[0][0]="Roll No"
            report_headings[0].append("Average")
            grades.pop(0)
            for grade in grades:
                flag = studentDetails.objects.filter(userid=grade[0],courseid=course,teacherid=request.session['person_id'])
                if flag:
                        grade[0]=studentDetails.objects.get(userid=grade[0],courseid=course,teacherid=request.session['person_id']).roll_no
                        report_details.append(grade)
                        tmarks=0.0
                        num=len(grade)
                        for j in range(4,num):
                                tmarks = tmarks + (float)(grade[j])# to be changed
                        avg=tmarks/float(num)
                        avg=round(avg,2)
                        grade.append(avg)
                        i=i+1
              totalstudents=i #student details table number of students associated
              if len(report_details):
                report_details.sort()
                quiz=range(1,len(report_details[0])-4)
                # Report header ,header - title of the report
                context = {'header':report_headings,'quiz':quiz,'totalstudents':totalstudents}
                context.update(pinfo)
                if option=="view":
                        print "view"
                        paginator=Paginator(report_details,15)
                        page=request.GET.get('page')
                        try:
                                pdata=paginator.page(page)
                        except PageNotAnInteger:
                                pdata = paginator.page(1)
                        except EmptyPage:
                                pdata=paginator.page(paginator.num_pages)
                        context['pdata']=pdata
                        return render(request, 'performance/report.html', context)
                elif option=="download":
                        print "download"
                        response = HttpResponse(content_type='text/csv')
                        courseid=edxcourses.objects.get(courseid=course).course
                        #timestr = time.strftime("%d-%m-%Y_%H:%M:%S")
                        timestr = datetime.now().strftime("%d-%m-%Y_%H:%M:%S")
                        fname = "%s_%s_%s" % ("report",courseid,timestr)
                         fname = fname + ".csv"
                        print fname
                        response['Content-Disposition'] = 'attachment; filename=%s'%fname
                        writer = csv.writer(response)
                        writer.writerows(report_headings)
                            writer.writerows(report_details)
                        return response
              else:
                message="!!! Empty Record !!!"
                print message
              '''
            message="!!! Empty Record !!!"
            return render(request, 'student/teacherhome.html', {'message':message})
def get_temp():
        a = []
        with open("/home/edx/docs/performance.csv","r") as f:
            reader = csv.reader(f)
            for row in reader:
                    a.append(row)
        return a

def reportinst(request,option,courseid):
        print "IN REPORTINST"
        pinfo = {}
        '''    pinfo.update(csrf(request))
            person=Personinformation.objects.get(email=request.session['email_id'])
             pinfo['firstname']=person.firstname
            pinfo['lastname']=person.lastname
            pinfo['email']=request.session['email_id']
            #coursename=Courselevelusers.objects.get(personid=request.session['person_id']).courseid.coursename
            course=edxcourses.objects.get(course=courseid).courseid
            #pinfo['coursename']=coursename
        #grades=getall_student_grades(course)
        # temp function to get grades from local system for testing
        grades=get_temp()
        #type
        performance_interface.objects.filter(courseid=course).delete()
        pinfo['teachername']=person.firstname+" "+person.lastname
        report_headings =[]
        #header=[]
        #data=[]
        report_details =[] 
        i=0
        report_headings.append(grades[0])
        report_headings[0][0]="Institute ID"
        report_headings[0][2]=report_headings[0][1]
        report_headings[0][1]="Institute Name"
        report_headings[0].append("Average")
        grades.pop(0)
        for grade in grades:
                flag = studentDetails.objects.filter(userid=grade[0],courseid=course)
                if flag:
                        teacher=studentDetails.objects.get(userid=grade[0],courseid=course).teacherid
                        person=Personinformation.objects.get(id=teacher.id).id
                        print person
                        instid=Courselevelusers.objects.get(personid=person,courseid__courseid=course,roleid=5).instituteid.instituteid
                        instname=Courselevelusers.objects.get(personid=person,courseid__courseid=course,roleid=5).instituteid.institutename
                        grade[0]=instid
                        grade[2]=grade[1]
                        instname=instname.replace(" "," ")
                        grade[1]=instname
                        print instname
                        report_details.append(grade)
                        tmarks=0.0
                        num=len(grade)
                        for j in range(4,num):
                                tmarks = tmarks + (float)(grade[j])# to be changed
                        avg=tmarks/float(num)
                        avg=round(avg,2)
                        grade.append(avg)
                        i=i+1
        totalstudents=i #student details table number of students associated
        if len(report_details):
                report_details.sort()
                quiz=range(1,len(report_details[0])-4)
                # Report header ,header - title of the report
                context = {'header':report_headings,'quiz':quiz,'totalstudents':totalstudents}
                context.update(pinfo)
                context['course']=courseid
                if option=="view":
                        print "view"
                        paginator=Paginator(report_details,15)
                        page=request.GET.get('page')
                        try:
                                pdata=paginator.page(page)
                        except PageNotAnInteger:
                                pdata = paginator.page(1)
                        except EmptyPage:
                                pdata=paginator.page(paginator.num_pages)
                        context['pdata']=pdata
                        print "RENDER"
                        return render(request, 'performance/reportinst.html', context)
                elif option=="download":
                        print "download"
                        response = HttpResponse(content_type='text/csv')
                        courseid=edxcourses.objects.get(courseid=course).course
                        #timestr = time.strftime("%d-%m-%Y_%H:%M:%S")
                        timestr = datetime.now().strftime("%d-%m-%Y_%H:%M:%S")
                        fname = "%s_%s_%s" % ("report",courseid,timestr)
                         fname = fname + ".csv"
                        print fname
                        response['Content-Disposition'] = 'attachment; filename=%s'%fname
                        writer = csv.writer(response)
                        writer.writerows(report_headings)
                            writer.writerows(report_details)
                        return response
        else:
                message="!!! No Records Found !!!" '''
        return render(request,'performance/courseadmin.html',{'message':message})


def reportinstcmp(request,option,courseid):
        pinfo = {}
        '''     pinfo.update(csrf(request))
            person=Personinformation.objects.get(email=request.session['email_id'])
             pinfo['firstname']=person.firstname
            pinfo['lastname']=person.lastname
            pinfo['email']=request.session['email_id']
            #coursename=Courselevelusers.objects.get(personid=request.session['person_id']).courseid.coursename
            course=edxcourses.objects.get(course=courseid).courseid
            #pinfo['coursename']=coursename
        #grades=getall_student_grades(course)
        # temp function to get grades from local system for testing
        grades=get_temp()
        #type
        performance_interface.objects.filter(courseid=course).delete()
        pinfo['teachername']=person.firstname+" "+person.lastname
        report_headings =[]
        #header=[]
        #data=[]
        report_details =[] 
        i=0
        report_headings.append(grades[0])
        report_headings[0][0]="Institute ID"
        report_headings[0][2]="Teacher Name"
        report_headings[0][1]="Institute Name"
        report_headings[0].pop(3)
        grades.pop(0)
        teachers=[]
        for grade in grades:
                flag = studentDetails.objects.filter(userid=grade[0],courseid=course)
                if flag:
                        teacher=studentDetails.objects.get(userid=grade[0],courseid=course).teacherid
                        person=Personinformation.objects.get(id=teacher.id).id
                        teachers.append(person)
        teachers=list(set(teachers))
        teachers.sort()
        for teacher in teachers:
                report_details.append([teacher])
        for grade in grades:
                flag = studentDetails.objects.filter(userid=grade[0],courseid=course)
                if flag:
                        teacher=studentDetails.objects.get(userid=grade[0],courseid=course).teacherid
                        person=Personinformation.objects.get(id=teacher.id).id
                        instid=Courselevelusers.objects.get(personid=person,courseid__courseid=course,roleid=5).instituteid.instituteid
                        instname=Courselevelusers.objects.get(personid=person,courseid__courseid=course,roleid=5).instituteid.institutename
                        index=teachers.index(person)
                        if len(report_details[index])==1:
                                report_details[index][0]=instid
                                report_details[index].append(instname)
                                teachername=Personinformation.objects.get(id=teacher.id).firstname+Personinformation.objects.get(id=teacher.id).lastname
                                report_details[index].append(teachername)
                                for i in range(4,len(grade)):
                                        report_details[index].append(int(grade[i]))
                                report_details[index].append(1)
                        else:
                                for i in range(4,len(grade)):
                                        report_details[index][i-1]=report_details[index][i-1]+int(grade[i])
                                report_details[index][len(report_details[index])-1]=report_details[index][len(report_details[index])-1]+1

        print report_details
        if len(report_details):
                for record in report_details:
                        num=len(record)
                        print num
                        print record[3],record[num-1]
                        total=record[num-1]
                        for i in range(3, num):
                                avg=record[i]/total
                                avg=round(avg,2)
                                record[i]=avg
                        record.pop()                
                quiz=range(1,len(report_details[0])-2)
                # Report header ,header - title of the report
                context = {'header':report_headings,'quiz':quiz}
                context.update(pinfo)
                context['course']=courseid
                if option=="view":
                        print "view"
                        paginator=Paginator(report_details,15)
                        page=request.GET.get('page')
                        try:
                                pdata=paginator.page(page)
                        except PageNotAnInteger:
                                pdata = paginator.page(1)
                        except EmptyPage:
                                pdata=paginator.page(paginator.num_pages)
                        context['pdata']=pdata
                        return render(request, 'performance/reportinstcmp.html', context)
                elif option=="download":
                        print "download"
                        response = HttpResponse(content_type='text/csv')
                        courseid=edxcourses.objects.get(courseid=course).course
                        #timestr = time.strftime("%d-%m-%Y_%H:%M:%S")
                        timestr = datetime.now().strftime("%d-%m-%Y_%H:%M:%S")
                        fname = "%s_%s_%s" % ("report",courseid,timestr)
                         fname = fname + ".csv"
                        print fname
                        response['Content-Disposition'] = 'attachment; filename=%s'%fname
                        writer = csv.writer(response)
                        writer.writerows(report_headings)
                            writer.writerows(report_details)
                        return response
        else:
                print "ERRRRRRRRRRR"
                message="!!! No Records Found !!!"'''
        return render(request,'performance/courseadmin.html',{'message':message})

def courseadmin(request):
        if request.method=='POST':
                report_type=request.POST['report_type']
                courseid=request.POST['course']
                if report_type=="college":
                        print "college"
                        return reportinst(request,"view",courseid)
                elif report_type=="compare":
                        print "compare"
                        return reportinstcmp(request,"view",courseid)
                else:
                        print "ERROR"
                        return render(request,'performance/courseadmin.html',input_list)
        input_list={}
        input_list.update(csrf(request))
        course_list=[]
        course_list_objects=edxcourses.objects.all()   #fetching all courses from database
        for course in course_list_objects:
                course_list.append(course.course)     
        input_list['course_list']=course_list 
        
        return render(request,'performance/courseadmin.html',input_list)





#######    performance module    #######
'''def warning(flag):
      if flag:
          return True
      else:
          args = {}
          args.update(csrf(request))
          args['form'] = form
          return render_to_response('performance/popup.html', args)'''

def storegrade(fname,course):
        fo=open(fname,'rb')    
        reader = csv.reader(fo)
        count = 0
        for record in reader:
                if count:
                        query = performance_interface(courseid=course,userid=record[0],email=record[1],username=record[2],grade=record[3])
                        query.save()                        
                        lenq = len(record)
                        while lenq > 4:
                                quiz = "quiz"+str(lenq-4)
                                marks = record[lenq-1]
                                user_id = record[0]
                                performance_interface.objects.filter(courseid=course,userid=user_id).update(**{quiz:marks})
                                lenq = lenq - 1
                count = count + 1

def gradeupload(request):
    
    if request.POST:
        form = UploadForms(request.POST, request.FILES)
        if form.is_valid():
            a = form.save()
            for p in uploadedfiles.objects.raw('SELECT * FROM SIP_uploadedfiles where uploadedby_id = 1 ORDER BY id DESC LIMIT 1 '):
                fname = str(p.filename)
            extension = validate_file_extension(fname)
            if(extension):
                course = request.POST['course']
                filetype = request.POST['filetype']
                if filetype=="performance":
                        invalid = 0;
                        fo=open(fname,'rb')    
                        reader = csv.reader(fo)
                        count = 0;
                        for record in reader:
                                if count:
                                        userid = record[0]
                                        email = record[1]
                                        username = record[2]
                                        isvalid = validate(userid,username,email)
                                        if not isvalid:        
                                                invalid = invalid + 1
                                count = count + 1 
                        if invalid:
                                message = "!!! "+str(invalid)+" Invalid Records Found !!!\n\t\t!!! Please Upload the correct Records !!!"
                                form = UploadForms()
                                args = {}
                                args.update(csrf(request))
                                args['form'] = form
                                args['message'] = message
                                return render_to_response('performance/gradeupload.html', args)
                        else:
                                '''obj = performance_interface.objects.filter(courseid=course)
                                if obj:
                                        flag = warning(False)
                                else:
                                        flag = True
                                if flag:'''
                                performance_interface.objects.filter(courseid=course).delete()
                                storegrade(fname,course)
                                result = "!!! GRADES UPLOADED !!!"
                                form = UploadForms()
                                args = {}
                                args.update(csrf(request))
                                args['form'] = form
                                args['result'] = result
                                return render_to_response('performance/gradeupload.html', args)
            else:
                message = " !!! Please Upload .csv File!!!"
                form = UploadForms()
                args = {}
                args.update(csrf(request))
    
                args['form'] = form
                args['message'] = message
                return render_to_response('performance/gradeupload.html', args)
           
    else:
        form = UploadForms()
        
    args = {}
    args.update(csrf(request))
    
    args['form'] = form
    
    return render_to_response('performance/gradeupload.html', args)


###################################################### blended mooc coordinator and admin   ############################################

#blended mooc coordinator
def bmchome(request):
        input_list={}
        input_list.update(csrf(request))
        errors=[]
        if request.method=='POST':
                input_list={}
                input_list.update(csrf(request))
                roles=[]
                rolenames=[]
                insta=[]
                input_list['errors']=errors
                input_list['institute_name']=request.POST.get('institute_name','')
                bmcvalidate(input_list)
                print request.POST.get('institute_name',''),"kkkkkkkkkkkkkkkkkkk"
                #validate bmc entries
                if not input_list['errors']:
                        input_list['institute_id']=(T10KT_Institute.objects.get(institutename=request.POST.get('institute_name'))).instituteid
                        print "institute",input_list['institute_id']
                        request.session['institute_id']=input_list['institute_id']
                        insti=Institutelevelusers.objects.filter(instituteid_id=(T10KT_Institute.objects.get(institutename=request.POST.get('institute_name')).instituteid))
                        instc=Courselevelusers.objects.filter(instituteid_id=(T10KT_Institute.objects.get(institutename=request.POST.get('institute_name')).instituteid))
                        for i in insti:
                                insta.append(i.roleid)
                        for i in instc:
                                insta.append(i.roleid)
                        print "deepak",insta
                        roles=set(insta)
                        for index in roles:
                                rolenames.append(Lookup.objects.get(category="Role",code=index).comment)
                        input_list['rolenames']=rolenames
                        input_list['flag']=False
                        return render(request,bmc_home_,input_list)
                else:
                        inst_name_list=[]
                        inst_list=T10KT_Approvedinstitute.objects.all()
                        for index in inst_list:
                                inst_name_list.append((T10KT_Institute.objects.get(instituteid=index.instituteid_id)).institutename)
                        input_list['inst_name_list']=inst_name_list
                        input_list['flag']=True
                        return render(request,bmc_home_,input_list)
        
        inst_name_list=[]
        inst_list=T10KT_Approvedinstitute.objects.all()
        for index in inst_list:
                inst_name_list.append((T10KT_Institute.objects.get(instituteid=index.instituteid_id)).institutename)
        input_list['inst_name_list']=inst_name_list
        input_list['flag']=True
        return render(request,bmc_home_,input_list)

def bmcintermediate(request,institute_id):
        request.session['institute_id']=institute_id
        input_list={}
        errors=[]
        input_list.update(csrf(request))
        input_list['role']=request.POST.get('role','')
        input_list['errors']=errors
        bmcrolevalidate(input_list)
        if not input_list['errors']:
                request.session['role_id']=Lookup.objects.get(category="Role",comment=request.POST.get('role')).code

                print request.session['role_id'],"aaaaaaaaaaaaaaaaaaaaa"
                return ccourse(request)
        else:
                render(request,bmc_home_,input_list)
#showing reports to blended mooc reports admin
def blendedadmin(request):
        if request.method=='POST':
                input_list={}
                input_list.update(csrf(request))
                errors=[]
                input_list['errors']=errors
                input_list['report_name']=request.POST.get('report_name')
                reportvalidate(input_list)
                if not input_list['errors']:
                        query=Reports.objects.get(report_title=input_list['report_name']).sqlquery
                        reports=Userlogin.objects.raw(query)
                        input_list['reports']=reports
                        return render(request,display_report_,input_list)
                report_name_list=[]
                report_list=Reports.objects.all()
                for index in report_list:
                        report_name_list.append(Reports.objects.get(reportid=index.reportid).report_title)
                        input_list['report_name_list']=report_name_list
                return render(request,admin_home_,input_list)
        input_list={}
        input_list.update(csrf(request))
        report_name_list=[]
        report_list=Reports.objects.all()   #fetching all reports from database
        for index in report_list:
                report_name_list.append(Reports.objects.get(reportid=index.reportid).report_title)     
        input_list['report_name_list']=report_name_list        #names of all reports to be displayed 
        return render(request,admin_home_,input_list)


############################################################  end blended mooc coordinator and admin   #########################################

@csrf_protect
def form1(request):
        args={}
        args.update(csrf(request))
        if request.method=="POST":
                #pwd1 = make_password(request.POST.get('passwd',''),salt=None,hasher='pbkdf2_sha256')
                singleuser=User.objects.create_user(username=request.POST.get('email'),email=request.POST.get('email'),password=request.POST.get('passwd',''))
                #x=User(email=request.POST.get('email'),password=pwd1)                
                singleuser.is_active=True  
                singleuser.save()   
                userprofile=Userlogin(user=singleuser,usertypeid=0)
                userprofile.save()
                HttpResponseRedirect('/')
        
        return render_to_response("intake form.html",args,context_instance=RequestContext(request))



########changepassword ##########################
def change_pass(request):
   
    module = 'Login'
    page = 'Reset_Pass'
    args={}
    args.update(csrf(request))
    if request.method == 'POST':
       args={}
       try: 
		   
		   args.update(csrf(request))
		   args['old_password']=oldpwd=request.POST.get('old_password','').strip()
		   user=User.objects.get(username=request.session['email_id'])
		   args['password1']=password1= request.POST.get('new_password1','').strip()
		   args['password2']=password2= request.POST.get('new_password2','').strip()
		   args['message']=[]
		   
		   per_id=Personinformation.objects.get(email=request.session['email_id']).id
		   if args['message']:
			  return render_to_response('login/changepass.html',args)
		   else: 
		         #args.update(csrf(request)
		         #user_auth=auth.authenticate(username=user.email,password=oldpwd)
		         if user.check_password(oldpwd):
			        
			        if  len(password1)==0 or len(password2)==0 or password1 != password2:
				        
				        args['message']= retrieve_error_message(module,page,'NO_MTCH')
				        return render_to_response('login/changepass.html',args)

			        else:  
		  ## If the two new passwords match, password is changed and a mail is sent to the user regarding the change 
				            
				        user.set_password(password1)
				        user.save()
                     
				        args['message']= retrieve_error_message(module,page,'PWD_SET')
				        ec_id = EmailContent.objects.get(systype='Login', name='success').id
				        send_email(ec_id, per_id, per_id)
                        
				        del request.session['person_id']
				        del request.session['email_id']
				        del request.session['institute_id']
				        request.session.flush()
				        cache.clear()
				        auth.logout(request)
		#return HttpResponseRedirect('/')
				        
				        #response['Cache-Control'] = 'no-cache, no-store, max-age=0, must-revalidate'
				        #response.delete_cookie()
	
				        return render_to_response('login/change_pwdsuccess.html',args)            
		         args['message']= "old password incorrect"
		         return render_to_response('login/changepass.html',args)
       except:
               
               args['error_message']="you are not logged in.Please login to change your password"
               return render_to_response('login/tologin.html',args)
    return  render_to_response('login/changepass.html',args)


#################################################









