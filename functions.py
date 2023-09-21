import os
import openai
import ast
from flask import jsonify

openai.organization = "org-qzg28Np9i12LTqFMRiAWrbAI"
openai.api_key = "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"


def generateIssue(summary):
  response = openai.ChatCompletion.create(
  model="gpt-4",
  messages=[
    {
      "role": "system",
      "content": "You need to identify the main problems only faced by the customer or complaints made by a customer from a series of customer and support executive exchanges and condense each separate issue to a single succinct, grammatically correct sentence and format it as \"Issue 1 $Issue 2 $Issue3\". Then, for each separate issue, write a short sentence explaining it and format it as a comma-separated array with each element corresponding to the respective issue [\"Sentence 1\", \"Sentence 2\"]. There should not be any full stops in the sentences and the sentences should be in double quotes. The final output must be formatted as  \"Issue1 $ Issue2 & [\"Sentence 1\",\"Sentence 2\"]\""
    },
    {
      "role": "user",
      "content": "The customer said that he could not contact his delivery partner and that the site took a long time to load."
    },
    {
      "role": "assistant",
      "content": "Cannot contact delivery partner $ Site takes a long time to load. & [\"The customer is unable to contact their delivery partner\", \"The website is slow to load\"]"
    },
    {
      "role": "user",
      "content": "The customer complained about his order reaching late and that there were too many ads in the app"
    },
    {
      "role": "assistant",
      "content": "Order delivered late $ Too many ads in the app. & [\"The customer's order arrived late\", \"The app has an excessive amount of advertisements\"]"
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
      "content": "target issue :  some images appear broken $ list of issues : [\"Unresponsive media players\", \"Inconsistent branding\" ,  \"Broken Images\" ,  \"Inconsistent Design\" , \"Outdated Content\", \"Lack of Accessibility\"]"
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

def generateTicket(text):
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



