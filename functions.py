import os
import openai
import ast
from flask import jsonify

openai.organization = "org-qzg28Np9i12LTqFMRiAWrbAI"
openai.api_key = "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"


def generateIssue(summary):
  response = openai.ChatCompletion.create(
  model="gpt-3.5-turbo",
  messages=[
    {
      "role": "system",
      "content": "You need to identify the main issues only faced by the customer or complaints made by a customer from a series of customer and support executive exchanges and condense it to a single grammatically correct sentence for each problem and display the output in such a way that i can parse it by splitting. Hence, show it in the format \"Issue 1$Issue 2$Issue3\""
    },
    {
      "role": "user",
      "content": " Customer: Hello! I am Rahul, I placed an order on swiggy 20 mins ago and I cannot reach my delivery executive. Executive: Give me a moment sir, let me just check. Customer: Sure! Executive: Thank you sir for being on hold, your order will take 15 more minutes to get ready as there is a rush at the restaurant. Your delivery executive is at the restaurant to collect the order as soon as he does it, he will contact you himself. Customer: But why can’t I reach my delivery executive? executive: As our delivery man hasn’t received your order yet from the restaurant and your delivery code hasn’t been generated so that’s why you are are unable to reach the delivery guy. Customer: But I wanted to customize my order a little. Executive: sir for the same you can contact the restaurant directly. The contact details are provided below your order. Customer: sure! Thank you for your help. Executive: It was my pleasure sir and we apologize for the inconvenience caused. I hope you enjoy your order and have a good day forth.  "
    },
    {
      "role": "assistant",
      "content": "Unable to reach delivery executive$Order delayed due to rush at restaurant$Unable to customize order through delivery executive"
    },
    {
      "role":"user",
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
  issues=reply.split('$')
  return issues


def findIssueMatch(request):
    body=request.json
    ticket=body['ticket']       #pass ticket creation event containing work field
    issues=body['issues']       #pass array of issues 
    summary=ticket['work']['body']
    id=ticket['work']['id']
    ticketIssues=generateIssue(summary)
    issueTitles=[]
    issueIds=[]
    print(ticketIssues)
    for issue in issues:
      issueTitles.append(issue['title'])
      issueIds.append(issue['id'])
    issueMap=[]
    unmatched=[]
    for ticketIssue in ticketIssues:
      flag=True
      result = matchesIssues(ticketIssue, str(issueTitles))
      for i in range(len(result)):
        if(result[i]==True and issueIds[i] not in issueMap):
          flag=False
          issueMap.append(issueIds[i])          #add isssue id if it matches any of the ticket issues
      if(flag==True):
        unmatched.append(ticketIssue)
    return {"issueIds" : issueMap, "issueNames":unmatched}


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
  return ast.literal_eval(reply)



