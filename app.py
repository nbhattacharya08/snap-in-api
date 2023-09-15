from flask import Flask , request
import requests
from twilio.twiml.voice_response import VoiceResponse

app = Flask(__name__)

@app.route("/", methods=['GET', 'POST'])
def meow():
    return "meow"

@app.route("/answer", methods=['GET', 'POST'])
def answer_call():
    """Respond to incoming phone calls with a brief message."""
    # Start our TwiML response
    resp = VoiceResponse()

    # Read a message aloud to the caller
    resp.say("Please record your message", voice='Polly.Amy')


    resp.record(action=" https://5c1b-202-142-106-83.ngrok-free.app/handleRecord",timeout=10, transcribe=True , transcribeCallback="https://cf79-202-142-106-83.ngrok-free.app/handleText" , channels=2)
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
    return "ok"
if __name__ == "__main__":
    app.run(debug=True)
