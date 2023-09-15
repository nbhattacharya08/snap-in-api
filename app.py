from flask import Flask , request
import requests
from twilio.twiml.voice_response import VoiceResponse

app = Flask(__name__)


@app.route("/answer", methods=['GET', 'POST'])
def answer_call():
    """Respond to incoming phone calls with a brief message."""
    # Start our TwiML response
    resp = VoiceResponse()

    # Read a message aloud to the caller
    resp.say("Please record your message", voice='Polly.Amy')


    resp.record(action="https://cf79-202-142-106-83.ngrok-free.app/handleRecord",timeout=10, transcribe=True , transcribeCallback="https://cf79-202-142-106-83.ngrok-free.app/handleText" , channels=2)
    print(resp)
    return str(resp)

@app.route("/handleRecord", methods=['GET', 'POST'])
def handleRecord():
    print(request)
    response=requests.get(request.body['RecordingUrl']+".mp3" , auth={"AC2deea27febf4d49d44979e23c46aad2c","AC2deea27febf4d49d44979e23c46aad2c"})
    if response.status_code == 200:
        # Extract the filename from the URL
        filename = file_url.split("/")[-1]

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
