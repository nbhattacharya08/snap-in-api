from flask import Flask , request
import requests
from functions import findIssueMatch , generateTicket
from twilio.twiml.voice_response import VoiceResponse , Dial
import openai
from dotenv import load_dotenv
import os

load_dotenv()


app = Flask(__name__)

@app.route("/", methods=['GET', 'POST'])
def meow():
    return "running"

@app.route("/answer", methods=['GET', 'POST'])
def answer_call():
    """Respond to incoming phone calls with a brief message."""
    # Start our TwiML response
    resp = VoiceResponse()

    # Read a message aloud to the caller
    #resp.say("Please record your message", voice='Polly.Amy')
    resp.say("Please record your message", voice='Polly.Amy')
    dial = Dial(
    record='record-from-answer-dual',
    recording_status_callback='https://hackerhive.onrender.com/handleRecord',
    timeout=30,
    channels=2
    )
    dial.number('+918981829798')
    resp.append(dial)
    print(resp)
    return str(resp)

@app.route("/handleRecord", methods=['GET', 'POST'])
def handleRecord():
    print(request.values)
    url=dict(request.values)
    url=url['RecordingUrl']+ ".mp3"
    print(url)
    response=requests.get(url , auth=("AC2deea27febf4d49d44979e23c46aad2c","fe472d53fb4ae0b7b0d7b29612a986dc"))
    print(response)
    filename=""
    if response.status_code == 200:
        # Extract the filename from the URL
        filename = url.split("/")[-1]

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

    config = {
            "Authorization": "eyJhbGciOiJSUzI1NiIsImlzcyI6Imh0dHBzOi8vYXV0aC10b2tlbi5kZXZyZXYuYWkvIiwia2lkIjoic3RzX2tpZF9yc2EiLCJ0eXAiOiJKV1QifQ.eyJhdWQiOlsiamFudXMiXSwiYXpwIjoiZG9uOmlkZW50aXR5OmR2cnYtdXMtMTpkZXZvL3lIeURwd3o0OmRldnUvMyIsImV4cCI6MTc4OTY1NTQzOCwiaHR0cDovL2RldnJldi5haS9hdXRoMF91aWQiOiJkb246aWRlbnRpdHk6ZHZydi11cy0xOmRldm8vc3VwZXI6YXV0aDBfdXNlci9nb29nbGUtb2F1dGgyfDEwOTgyODk4NTIwMzYxMjIyNzY4NSIsImh0dHA6Ly9kZXZyZXYuYWkvYXV0aDBfdXNlcl9pZCI6Imdvb2dsZS1vYXV0aDJ8MTA5ODI4OTg1MjAzNjEyMjI3Njg1IiwiaHR0cDovL2RldnJldi5haS9kZXZvX2RvbiI6ImRvbjppZGVudGl0eTpkdnJ2LXVzLTE6ZGV2by95SHlEcHd6NCIsImh0dHA6Ly9kZXZyZXYuYWkvZGV2b2lkIjoiREVWLXlIeURwd3o0IiwiaHR0cDovL2RldnJldi5haS9kZXZ1aWQiOiJERVZVLTMiLCJodHRwOi8vZGV2cmV2LmFpL2Rpc3BsYXluYW1lIjoibmlsYW5qYW5iaGF0dGFjaGFyeWEyMiIsImh0dHA6Ly9kZXZyZXYuYWkvZW1haWwiOiJuaWxhbmphbmJoYXR0YWNoYXJ5YTIyQGdtYWlsLmNvbSIsImh0dHA6Ly9kZXZyZXYuYWkvZnVsbG5hbWUiOiJOaWxhbmphbiBCaGF0dGFjaGFyeWEiLCJodHRwOi8vZGV2cmV2LmFpL2lzX3ZlcmlmaWVkIjp0cnVlLCJodHRwOi8vZGV2cmV2LmFpL3Rva2VudHlwZSI6InVybjpkZXZyZXY6cGFyYW1zOm9hdXRoOnRva2VuLXR5cGU6cGF0IiwiaWF0IjoxNjk1MDQ3NDM4LCJpc3MiOiJodHRwczovL2F1dGgtdG9rZW4uZGV2cmV2LmFpLyIsImp0aSI6ImRvbjppZGVudGl0eTpkdnJ2LXVzLTE6ZGV2by95SHlEcHd6NDp0b2tlbi9iMk8xNk5jZSIsIm9yZ19pZCI6Im9yZ19IVlBYWUFOUFNpcDFKQ1lYIiwic3ViIjoiZG9uOmlkZW50aXR5OmR2cnYtdXMtMTpkZXZvL3lIeURwd3o0OmRldnUvMyJ9.riTCPgsDXHESE7Icomvg5dZSxE_iYq_W5zBIMM1X8hgq_4sx-myiGE8c4XJy5w3_binwhFCU15ippOyUlJ9PcY2A8YNtX8RHb93K0R4RZ1SEI33YfMEupbvDjN46SXcQS8sItyrWLiy2ewXHH0J2J0TB7JWaiSRPQG6hgHg7ConkqDcLLPcW77GUyesancMOlWxWpJX3jWqyRovUDQ8HRuA67iKGApjn7zda-9cbxYcMopwI_hebCgRAbZR7OCW-ZpesQ2HwOrfpsoqNoqr86Zd13seLNHqAbMwbCDddiaW298FIj5FhEAwuPgwyeVyU-qSjUaF8EPAm1FLBcJBDxQ",
            "Content-Type": 'application/json'
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
    generateTicket(transcript["text"] , id)

    return transcript["text"]


@app.route("/group-issue",methods=["POST"])
def handleGroupIssue():
    return findIssueMatch(request)

        
if __name__ == "__main__":
    app.run(debug=True,port=os.getenv("PORT",5000),host="0.0.0.0")

