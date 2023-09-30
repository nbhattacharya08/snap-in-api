from flask import Flask , request
import requests
from functions import findIssueMatch , generateTicket , mycoll , supportColl
from twilio.twiml.voice_response import VoiceResponse , Dial
import openai
from dotenv import load_dotenv
import os

load_dotenv()


app = Flask(__name__)

custNum=""
ticketId=""
@app.route("/", methods=['GET', 'POST'])
def meow():
    return "running"

@app.route("/answer", methods=['GET', 'POST'])
def answer_call():
    """Respond to incoming phone calls with a brief message."""
    # Start our TwiML response
    resp = VoiceResponse()
    print(request)
    config =  {
    'Authorization': os.getenv("DEVREV_TOKEN")
    }
    # Read a message aloud to the caller
    #resp.say("Please record your message", voice='Polly.Amy')
    resp.say("Hello, this is the waiting room", voice='Polly.Amy')
    print("call event\n",request)
    cnum=request.form["From"]
    if(supportColl.find_one({"number":cnum}) != None):
         #change to if number is in service centre db
        resp.say("Please wait while we connect you to our support executive")
        print("from",cnum)
        dial = Dial(
        record='record-from-answer-dual',
        recording_status_callback= 'https://b742-103-44-174-33.ngrok-free.app/commandRecord',
        timeout=30,
        channels=2,
        caller_id="+12564856295"
        )
        dial.number(os.getenv("CUSTOMER_SUPPORT_NO"))
    else:
        #if number is not in customer database go to handleRecord 
        #if number is in customer database and ticket is closed then create new ticket,delete entry in cust db and go to handleRecord
        #if number is in customer database and ticket is open go to command record
        if(mycoll.find_one({"number":cnum}) == None):
            dial = Dial(
            record='record-from-answer-dual',
            recording_status_callback='    https://b742-103-44-174-33.ngrok-free.app/handleRecord',
            timeout=30,
            channels=2,
            caller_id="+12564856295"
            )
            dial.number(os.getenv("CUSTOMER_SUPPORT_NO"))
        else :
            query=mycoll.find_one({"number":cnum})
            result=requests.post(f"https://api.devrev.ai/works.get?id={query['ticket_id']}", headers=config)
            stage=result.json()['work']['stage']['name']
            print(stage)
            if(stage=="accepted" or stage=="resolved" or stage=="cancelled"):
                mycoll.delete_one({"ticket_id":query['ticket_id']})
                dial = Dial(
                record='record-from-answer-dual',
                recording_status_callback=' https://b742-103-44-174-33.ngrok-free.app/handleRecord',
                timeout=30,
                channels=2,
                caller_id="+12564856295"
                )
                dial.number(os.getenv("CUSTOMER_SUPPORT_NO"))
            else:
                global ticketId
                ticketId=query['ticket_id']
                dial = Dial(
                record='record-from-answer-dual',
                recording_status_callback=' https://b742-103-44-174-33.ngrok-free.app/commandRecord',
                timeout=30,
                channels=2,
                caller_id="+12564856295"
                )
                dial.number(os.getenv("CUSTOMER_SUPPORT_NO"))
                
    resp.append(dial)
    print(resp)
    return str(resp)

@app.route("/handleRecord", methods=['GET', 'POST'])
def handleRecord():
    print(request.values)
    url=dict(request.values)
    sid=url["CallSid"]
    print(url["CallSid"])
    url=url['RecordingUrl']+ ".mp3"
    print(url)
    response=requests.get(url , auth=(os.getenv("TWILIO_SID"),os.getenv("TWILIO_TOKEN")))
    print(response)
    filename=sid+".mp3"
    if response.status_code == 200:
        
        # Specify the local path where you want to save the downloaded file
        local_path = f'./{filename}'  # You can customize this path

        # Write the content of the response (file) to the local file
        with open(local_path, 'wb') as file:
            file.write(response.content)

        print(f"File '{filename}' downloaded successfully to '{local_path}'")

    else:
        print(f"Failed to download file. Status code: {response.status_code}")
        
    
    openai.api_key = os.getenv("OPENAI_API_KEY")
    audio_file= open(f'./{filename}', "rb")
    transcript = openai.Audio.transcribe("whisper-1", audio_file)
    print(transcript)

    config =  {
    'Authorization': os.getenv("DEVREV_TOKEN"),
    'Content-Type': 'application/json'
    }

    r = requests.post("https://api.devrev.ai/artifacts.prepare" , json={"file_name":filename} , headers=config)
    r=r.json()
    id=r["id"]
    form = r["form_data"]
    link=r["url"]
    formdata={}

    for i in form:
        formdata[i["key"]]=i["value"]
    with open(f'./{filename}' , "rb") as file:
        requests.post(link , data=formdata , files={"file":file})

    #transcript["text"]="Hello. Hello, I am calling about an order on a food delivery app. Yeah, could you tell me what problem you are facing? I can't contact my delivery partner. Alright, just give me a second, I will look into it. Yeah, hello sir, your delivery partner has been assigned and they will contact you shortly. Are you facing any other problem? There were a lot of spelling errors in your website. Alright, fine, I will have my team look at it. Okay. Thank you."
    generateTicket(transcript["text"] , id , sid)

    return transcript["text"]


@app.route("/group-issue",methods=["POST"])
def handleGroupIssue():
    return findIssueMatch(request)

@app.route("/set-number",methods=["POST"])
def handleSetNumber():
    global ticketId,custNum
    req=request.json
    custNum=req["custNum"]
    ticketId=req["ticketId"]
    return "successfully sent"

@app.route("/commandRecord",methods=["GET", "POST"])
def handleCommandRecord():
    global ticketId
    url=dict(request.values)
    sid=url["CallSid"]
    print(url["CallSid"])
    url=url['RecordingUrl']+ ".mp3"
    print(url)
    response=requests.get(url , auth=(os.getenv("TWILIO_SID"),os.getenv("TWILIO_TOKEN")))
    print(response)
    filename=sid+".mp3"
    if response.status_code == 200:
        # Specify the local path where you want to save the downloaded file
        local_path = f'./{filename}'  # You can customize this path

        # Write the content of the response (file) to the local file
        with open(local_path, 'wb') as file:
            file.write(response.content)

        print(f"File '{filename}' downloaded successfully to '{local_path}'")

    else:
        print(f"Failed to download file. Status code: {response.status_code}")

    config =  {
    'Authorization': os.getenv("DEVREV_TOKEN"),
    'Content-Type': 'application/json'
    }

    r = requests.post("https://api.devrev.ai/artifacts.prepare" , json={"file_name":filename} , headers=config)
    r=r.json()
    artid=r["id"]
    form = r["form_data"]
    link=r["url"]
    formdata={}
    print(ticketId+" hi")
    for i in form:
        formdata[i["key"]]=i["value"]
    with open(f'./{filename}' , "rb") as file:
        requests.post(link , data=formdata , files={"file":file})
    
    res= requests.get(f"https://api.devrev.ai/works.get?id={ticketId}",headers=config)
    res=res.json()
    print(res)
    reqArr=res["work"]["artifacts"]
    artifactIds=[]
    for art in reqArr:
        artifactIds.append(art["id"])
    artifactIds.append(artid)
    res=requests.post("https://api.devrev.ai/works.update",json={"id":ticketId,"artifacts":{"set":artifactIds}},headers=config)
    return res.json()
    
        

        
if __name__ == "__main__":
    app.run(debug=True,port=os.getenv("PORT",5000),host="0.0.0.0")

