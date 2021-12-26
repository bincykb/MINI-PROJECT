import json
import urllib
from flask import Flask, request, render_template,session
import re
#from translate import Translator

import infermedica_api
global diagnosis, symptom
#21794b8d
#81f5f69f0cc9d2defaa3c722c0e905bf

api = infermedica_api.configure(app_id='951f8eec', app_key='36aa3e0bef04d58f99c8d1172c0bcfea')
#print(api.info())

app = Flask(__name__)

app.secret_key = 'ana#ghac45ot'


#translator=Translator(from_lang='en',to_lang='ml')
symptom_mode = False
symptom = None
gender = None
age = None
diagnosis = None
evidence = [
            {"id": "s_21", "choice_id": "present", "source": "initial"},
            {"id": "s_98", "choice_id": "present", "source": "initial"},
            {"id": "s_107", "choice_id": "present"}
        ]

@app.route("/")
def index():
   
   if not 'info' in session:
      info= api.info()
      session['info']=info
   else :
      info=session['info']
              
   return render_template("index.html",info=api.info())

@app.route("/about/")
def about():
   return render_template("about.html")

@app.route("/service/")
def service():
   clinicsURL ="https://api.foursquare.com/v2/venues/search?ll=10.528402,76.211854&radius=15000&query=hospital&client_id=1TCDH3ZYXC3NYNCRVL1RL4WEGDP4CHZSLPMKGCBIHAYYVJWA&client_secret=VASKTPATQLSPXIFJZQ0EZ4GDH2QAZU1QGEEZ4YDCKYA11V2J&v=20160917"
   #r = urllib.urlopen(clinicsURL)


   r=urllib.request.urlopen(clinicsURL)
   data = json.loads(r.read())
   venues = data["response"]["venues"]
   #venues=[{'name':'abc','location':'xyz'}]
   return render_template("service.html",venu=venues)

@app.route("/sample/")
def sample():
   return render_template("sample.html")

@app.route("/cardiology/")
def cardiology():
   return render_template("cardiology.html")

@app.route("/neurology/")
def neurology():
   return render_template("neurology.html")

@app.route("/oncology/")
def oncology():
   return render_template("oncology.html")

@app.route("/orthopeadics/")
def orthopeadics():
   return render_template("orthopeadics.html")

@app.route("/outpatient/")
def outpatient():
   return render_template("outpatient.html")

@app.route("/mentalhealth/")
def mentalhealth():
   return render_template("mentalhealth.html")

@app.route("/contact/")
def contact():
   return render_template("contact.html")

@app.route("/appointment/")
def appointment():
   return render_template("appointment.html")

@app.route("/reminder/")
def reminder():
   return render_template("reminder.html")


@app.route("/test3/", methods=["POST"])
def input_evaulation():
    session["evidence"] = evidence
    session["stop_asking"] = False
    if "messages" in session:
        messages = list(session["messages"])
    else:
        messages = []

    user_input = request.form.get("msg")
    
    if not user_input:
        no_input_provided = ["Please provide a valid input"]
        return render_template("test3.html", msgs=no_input_provided)

    if not messages:
        gender, age = [_input.lower().strip()for _input in user_input.split(",")]
        if gender not in ["male", "female"]:
            no_input_provided = ["Please provide a valid input"]
            return render_template("test3.html", msgs=no_input_provided)
        session["age"] = age
        session["gender"] = gender
    else:
        
        for option in session["last_options"]:
            option_text = option["name"]
            if user_input.strip().lower() == option_text.lower():
                new_evidence = {"id": option["id"], "choice_id": "present"}
                session["evidence"].append(new_evidence) 
        
        if user_input.strip().lower() == "don't know":
            new_evidence = {"id": option["id"], "choice_id": "unknown"}
            session["evidence"].append(new_evidence) 
        if user_input.strip().lower() == "no":
            new_evidence = {"id": option["id"], "choice_id": "absent"}
            session["evidence"].append(new_evidence) 
            
    if session["stop_asking"]:
        show_conditions = "Your diagnosis is as follows:<br/>"
        for condition in session["conditions"]:
            probability = condition["probability"] * 100
            show_conditions.append([condition["common_name"], f"{probability}%"])
       
        messages.append(["", show_conditions])
        return render_template("test3.html", msgs=messages)
    
    try:
        api_response = api.diagnosis(evidence=session["evidence"], sex=session["gender"], age=session["age"])
    except Exception as why:
        print(why)
        messages = ["The service is not responding. Plesae reload the page and try again.", ""]
        return render_template("test3.html", msgs=messages)
    should_stop = api_response["should_stop"]
    session["stop_asking"] = should_stop
    with open("test.json", "w") as wf:
        json.dump(api_response, wf, indent=2)
    display_response = api_response["question"]["text"]
    display_response += "&nbsp;Select your choice: Choose No if None match or Don't know if you are not sure<br/><ul>"
    for item in api_response["question"]["items"]:
        display_response += "<li>" + item["name"] + "</li>"
    
    display_response += "<li>No</li>"
    display_response += "<li>NA</li>"
    display_response += "</ul>"
    messages.append([user_input, display_response])
    session["messages"] = messages
    session["last_options"] = api_response["question"]["items"]
    session["conditions"] = api_response["conditions"]
    return render_template("test3.html", msgs=messages)

@app.route("/test3/",methods=['GET'])
def test3():
   
   msg=[]
   if request.method == 'GET':
       session.clear()
       
   if request.method == 'POST':
      msg=[] # retrieve from session
      
      if 'msg' in session:
         msg=list(session['msg'])

      m=request.form.get('msg')
      
      if m!=None:
         r="...I am hearing..!But i didn't understand..."
         if 'gndr' not in session and 'age' not in session:
            if 'male' not in m.lower():
               r='your gender and age please as gender,age'
            else:
               s=m.split(',')
               if len(s)!=2 or s[0] =='' or s[1]==''  :
                  r='your gender and age please as gender,age'
               else:
                  session['gndr']=s[0].lower()
                  session['age']=s[1]
                  r='What concerns you most about your health?Please describe your symptoms..<br/> Later i will ask you a couple of questions,\nPlease answer either yes or no.'
         elif not 'q' in session:
            if 'sreq' not in session :
               srq=[]
            else :
               srq=session['sreq']
           
            br=[]
            z=(br.append( j.split(' ')) for j in m.split(',') if j !='')

            for i in br:
               #for j in i:
               if i not in srq:
                     srq.append(i)
            if srq :
               session['sreq']=srq;
           
##            if not 'sym' in session:
##               s=api.symptoms_list()
##               session['sym']=s
##            else :
##               s=session['sym']
            
            s = api.symptom_list(session['age'])

            g = []

            for i in s:
               #f=True
               for j in srq:    
                  n=re.search(r'\b({})\b'.format(j.lower()), i['name'].lower())
                  if n!=None :
                   #if j.lower()  in i['name'].lower():
                     sd=api.symptom_details(i['id'],session['age'])
                     g.append({'id':i['id'],'qn':sd.get('question'),'ans':''})
               #if f :
               
            print(g)  
            if g:
               session['q']=g
               r= g[0]['qn']
         else :
             q=session['q']
             
             r=''
             
             mc=m
             for i in q:
                if i['qn']!='' and i['ans']=='' and r=='':
                   if mc!='' :
                      
                      if mc.lower()=='yes':
                         i['ans']=mc
                      else :
                         i['ans']='no'
                      mc=''
                   else:
                      r=i['qn']
             if r==''  :
                  sx=session['gndr']
                  ag=session['age']
                  
                  #req = infermedica_api.Diagnosis(sex=sx, age=ag)
                  #for i in q:
                     #if i['qn']=='' or i['ans']=='yes' :
                        #req.add_symptom(i['id'], 'present', initial=True)
                  #if req:
                  cn=api.diagnosis(evidence=evidence,sex=sx,age=ag)
                  if cn:
                        r='Your situation is analysed as \n'+cn["conditions"][0]["name"]+'\n with common name:'+cn["conditions"][0]["common_name"]
                        if 'extras' in cn["conditions"][0]:
                           if 'hint' in cn["conditions"][0]['extras']:
                              r+='\n'+cn["conditions"][0]['extras']['hint']
                  else:
                        r="need more specific info about your illness, which part, how you feel etc."

                  session.pop('q', None)
                  session.pop('sreq',None)
                  #relmsg=True
               #else:
                  #r='some more cliarification needed. specify the area and illness feeling'
                  
         t=(m,r)
         msg.append(t)
         session['msg']=msg 
         #m=translator.translate(msg)
         
##         if not relmsg :
##            session['msg']=msg #assign new msg to session
##         else :
##            mg=list(msg)
##            session.pop('msg',None)
##            msg=mg
   
      #log(msg)
      #return(msg)
      
   
   return render_template("test3.html",msgs=msg)

    
   #if 'msg' in Session:
    #  m = Session['msg']
     # if m!=None:
      #   msg.append(m)

if __name__ == '__main__':
    app.run(debug=True)
