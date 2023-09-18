from flask import Flask , request, jsonify
import requests
from functions import findIssueMatch
from twilio.twiml.voice_response import VoiceResponse , Dial
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
    recording_status_callback='https://5c1b-202-142-106-83.ngrok-free.app/handleRecord',
    timeout=30,
    channels=2
    )
    dial.number('+918336953155')
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
        
    print(os.getenv("OPENAI_API_KEY"))
    openai.api_key = os.getenv("OPENAI_API_KEY")
    audio_file= open(f'./{filename}', "rb")
    transcript = openai.Audio.transcribe("whisper-1", audio_file)
    print(transcript)

    return transcript["text"]


@app.route("/group-issue",methods=["POST"])
def handleGroupIssue():
    return jsonify(findIssueMatch(request))
    
if __name__ == "__main__":
    app.run(debug=True)
