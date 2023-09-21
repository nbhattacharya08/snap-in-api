import os
import openai
import ast
from flask import jsonify
import requests

openai.organization = "org-qzg28Np9i12LTqFMRiAWrbAI"
openai.api_key = "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"


def generateIssue(summary):
  response = openai.ChatCompletion.create(
  model="gpt-4",
  messages=[
    {
      "role": "system",
      "content": "You need to identify the main problems only faced by the customer or complaints made by a customer from a series of customer and support executive exchanges and condense each separate issue to a single succinct, grammatically correct sentence and format it as \"Issue 1$Issue 2$Issue3\". Then, for each separate issue, write a short sentence explaining it and format it as a comma-separated array with each element corresponding to the respective issue [Sentence 1, Sentence 2]. The final output must be formatted as  \"Issue1$Issue2 & [Sentence 1,Sentence 2]\""
    },
    {
      "role": "user",
      "content": "The customer contacts the customer care executive to report two issues. The first issue is that they are unable to contact their assigned delivery partner. The executive assures the customer that the delivery partner will be in touch soon. The second issue is about spelling errors on the food delivery app's website. The executive acknowledges the problem and assures the customer that their team will address it. The call concludes with the customer expressing their gratitude."
    },
    {
      "role": "assistant",
      "content": "Unable to contact delivery partner $ Spelling errors on website & [\"The customer is unable to contact the assigned delivery partner\", \"There are spelling errors on the website\"]"
    },
    {
      "role": "user",
      "content": "The customer contacts the customer care executive to report two issues with a music listening app. The first issue is that they are unable to view their playlists in the app. The executive informs the customer that there is a bug currently being worked on and appreciates the customer's patience. The second issue is that some songs are not available on the app, to which the executive explains that it is due to policy changes. The call concludes with the customer expressing gratitude and ending the call. "
    },
    {
      "role": "assistant",
      "content": "Playlists not visible $ Unavailable songs & [\"The customer cannot view their playlists\", \"Some songs are not available due to policy changes\"]"
    },
    {
      "role": "user",
      "content": summary
    }
  ],
  temperature=1,
  max_tokens=256,
  top_p=1,
  frequency_penalty=0,
  presence_penalty=0
)
  reply=response['choices'][0]['message']['content']
  reply=reply.split('&')
  return {"issues":reply[0].split('$'), "text":ast.literal_eval(reply[1].strip())}


def findIssueMatch(request):
    body=request.json
    ticket=body['ticket']       #pass ticket creation event containing work field
    issues=body['issues']       #pass array of issues 
    summary=ticket['work']['body']
    id=ticket['work']['id']
    generatedIssues=generateIssue(summary)
    ticketIssues=generatedIssues["issues"]
    issueText=generatedIssues["text"]
    issueTitles=[]
    issueIds=[]
    issueBody=[]
    print(ticketIssues)
    for issue in issues:
      issueTitles.append(issue['title'])
      issueIds.append(issue['id'])
    issueMap=[]
    unmatched=[]
    j=0
    for ticketIssue in ticketIssues:
      flag=True
      result = matchesIssues(ticketIssue, str(issueTitles))
      for i in range(len(result)):
        if(result[i]==True and issueIds[i] not in issueMap):
          flag=False
          issueMap.append(issueIds[i])          #add isssue id if it matches any of the ticket issues
      if(flag==True):
        unmatched.append(ticketIssue)
        issueBody.append(issueText[j])
      j=j+1
    return {"issueIds" : issueMap, "issueNames":unmatched, "issueBody": issueBody}  #add issueBody field


def matchesIssues(ticketIssue,issues):
  question = "target phrase : "+ticketIssue + " $ list of issues : "+issues
  response = openai.ChatCompletion.create(
  model="gpt-4",
  messages=[
    {
      "role": "system",
      "content": "You are given a list of issues and a single phrase. Return \"True\" if a pair of phrases convey the same meaning or roughly point to the same issue associated with a component or feature, else return \"False\". The output must be formatted in the following way \"[True, False, True]\" where a true value denotes that the issue at that index matches the target phrase. The target phrase and the list of issues are separated by \"$\""
    },
    {
      "role": "user",
      "content": "target issue : some images appear broken $ list of issues : [\"Unresponsive media players\", \"Inconsistent branding\" ,  \"Broken Images\" ,  \"Inconsistent Design\" , \"Outdated Content\", \"Lack of Accessibility\"]"
    },
    {
      "role": "assistant",
      "content": "[False, False, True, False, False, False]"
    },
    {
      "role": "user",
      "content": question
    }
  ],
  temperature=1,
  max_tokens=256,
  top_p=1,
  frequency_penalty=0,
  presence_penalty=0
  )
  reply=response['choices'][0]['message']['content']
  return ast.literal_eval(reply.strip())

def generateTicket(text , id):
  response = openai.ChatCompletion.create(
    model="gpt-4",
    messages=[
      {
        "role": "system",
        "content": "You are given a transcript of a call between a customer care executive and a customer. Infer the customer's dialogues and provide a summary of the call. Then, provide a short title for the summary. The output must be formatted in the following way\n\"Summary $ Title\""
      },
      {
        "role": "user",
        "content": "Hello. Hello, I am calling about an order on a food delivery app. Yeah, could you tell me what problem you are facing? I can't contact my delivery partner. Alright, just give me a second, I will look into it. Yeah, hello sir, your delivery partner has been assigned and they will contact you shortly. Are you facing any other problem? There were a lot of spelling errors in your website. Alright, fine, I will have my team look at it. Okay. Thank you."
      },
      {
        "role": "assistant",
        "content": "The customer contacts the customer care executive to report two issues. The first issue is that they are unable to contact their assigned delivery partner. The executive assures the customer that the delivery partner will be in touch soon. The second issue is about spelling errors on the food delivery app's website. The executive acknowledges the problem and assures the customer that their team will address it. The call concludes with the customer expressing their gratitude. $  Food delivery issue and spelling errors."
      },
      {
        "role": "user",
        "content": "Hello. Hi, I am calling about an issue on a music listening app. Could you tell me what the problem is? I cant view my playlists in the app. We are working on that bug currently, thank you for your patience. Some songs are also not available on the app. That is due to some policy changes, Sir. Okay, Thank you. Bye."
      },
      {
        "role": "assistant",
        "content": "The customer contacts the customer care executive to report two issues with a music listening app. The first issue is that they are unable to view their playlists in the app. The executive informs the customer that there is a bug currently being worked on and appreciates the customer's patience. The second issue is that some songs are not available on the app, to which the executive explains that it is due to policy changes. The call concludes with the customer expressing gratitude and ending the call. $ Playlist visibility issue and unavailable songs."
      },
      {
        "role": "user",
        "content": text
      }
    ],
    temperature=1,
    max_tokens=256,
    top_p=1,
    frequency_penalty=0,
    presence_penalty=0
  )
  response=response['choices'][0]['message']['content']
  ticket_body=response.split('$')[0].strip()
  ticket_name=response.split('$')[1].strip()
  config =  {
    'Authorization': "eyJhbGciOiJSUzI1NiIsImlzcyI6Imh0dHBzOi8vYXV0aC10b2tlbi5kZXZyZXYuYWkvIiwia2lkIjoic3RzX2tpZF9yc2EiLCJ0eXAiOiJKV1QifQ.eyJhdWQiOlsiamFudXMiXSwiYXpwIjoiZG9uOmlkZW50aXR5OmR2cnYtdXMtMTpkZXZvL3lIeURwd3o0OmRldnUvMyIsImV4cCI6MTc4OTY1NTQzOCwiaHR0cDovL2RldnJldi5haS9hdXRoMF91aWQiOiJkb246aWRlbnRpdHk6ZHZydi11cy0xOmRldm8vc3VwZXI6YXV0aDBfdXNlci9nb29nbGUtb2F1dGgyfDEwOTgyODk4NTIwMzYxMjIyNzY4NSIsImh0dHA6Ly9kZXZyZXYuYWkvYXV0aDBfdXNlcl9pZCI6Imdvb2dsZS1vYXV0aDJ8MTA5ODI4OTg1MjAzNjEyMjI3Njg1IiwiaHR0cDovL2RldnJldi5haS9kZXZvX2RvbiI6ImRvbjppZGVudGl0eTpkdnJ2LXVzLTE6ZGV2by95SHlEcHd6NCIsImh0dHA6Ly9kZXZyZXYuYWkvZGV2b2lkIjoiREVWLXlIeURwd3o0IiwiaHR0cDovL2RldnJldi5haS9kZXZ1aWQiOiJERVZVLTMiLCJodHRwOi8vZGV2cmV2LmFpL2Rpc3BsYXluYW1lIjoibmlsYW5qYW5iaGF0dGFjaGFyeWEyMiIsImh0dHA6Ly9kZXZyZXYuYWkvZW1haWwiOiJuaWxhbmphbmJoYXR0YWNoYXJ5YTIyQGdtYWlsLmNvbSIsImh0dHA6Ly9kZXZyZXYuYWkvZnVsbG5hbWUiOiJOaWxhbmphbiBCaGF0dGFjaGFyeWEiLCJodHRwOi8vZGV2cmV2LmFpL2lzX3ZlcmlmaWVkIjp0cnVlLCJodHRwOi8vZGV2cmV2LmFpL3Rva2VudHlwZSI6InVybjpkZXZyZXY6cGFyYW1zOm9hdXRoOnRva2VuLXR5cGU6cGF0IiwiaWF0IjoxNjk1MDQ3NDM4LCJpc3MiOiJodHRwczovL2F1dGgtdG9rZW4uZGV2cmV2LmFpLyIsImp0aSI6ImRvbjppZGVudGl0eTpkdnJ2LXVzLTE6ZGV2by95SHlEcHd6NDp0b2tlbi9iMk8xNk5jZSIsIm9yZ19pZCI6Im9yZ19IVlBYWUFOUFNpcDFKQ1lYIiwic3ViIjoiZG9uOmlkZW50aXR5OmR2cnYtdXMtMTpkZXZvL3lIeURwd3o0OmRldnUvMyJ9.riTCPgsDXHESE7Icomvg5dZSxE_iYq_W5zBIMM1X8hgq_4sx-myiGE8c4XJy5w3_binwhFCU15ippOyUlJ9PcY2A8YNtX8RHb93K0R4RZ1SEI33YfMEupbvDjN46SXcQS8sItyrWLiy2ewXHH0J2J0TB7JWaiSRPQG6hgHg7ConkqDcLLPcW77GUyesancMOlWxWpJX3jWqyRovUDQ8HRuA67iKGApjn7zda-9cbxYcMopwI_hebCgRAbZR7OCW-ZpesQ2HwOrfpsoqNoqr86Zd13seLNHqAbMwbCDddiaW298FIj5FhEAwuPgwyeVyU-qSjUaF8EPAm1FLBcJBDxQ",
    'Content-Type': 'multipart/form-data'
    }
  res=requests.post("https://api.devrev.ai/works.create",{"artifacts":[id] , "body":ticket_body,"title":ticket_name , type:"ticket"},headers=config)
  return res.json()


