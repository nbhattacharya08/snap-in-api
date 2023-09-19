import os
import openai

openai.organization = "org-qzg28Np9i12LTqFMRiAWrbAI"
openai.api_key = "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"


def generateIssue(summary):
  response = openai.ChatCompletion.create(
  model="gpt-3.5-turbo",
  messages=[
    {
      "role": "system",
      "content": "You need to identify the main problems only faced by the customer or complaints made by a customer from a series of customer and support executive exchanges and condense it to a single grammatically correct sentence for each problem and display the output in such a way that i can parse it by splitting. Hence, show it in the format \"Issue 1$Issue 2$Issue3\""
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



def matchesIssue(issue, ticketIssue):
  question = issue + "$" + ticketIssue
  response = openai.ChatCompletion.create(
  model="gpt-4",
  messages=[
    {
      "role": "system",
      "content": "Return \"True\" if the two phrases convey the same meaning or roughly point to the same issue associated with a component or feature, else return \"False\". The two phrases are separated by '$'"
    },
    {
      "role": "user",
      "content": "Unresponsive submit button $ submit button not working properly"
    },
    {
      "role": "assistant",
      "content": "True"
    },
    {
      "role": "user",
      "content": "Poor UI design $ Interface is not user friendly"
    },
    {
      "role": "assistant",
      "content": "True"
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

  return reply



def findIssueMatch(request):
    body=request.json
    ticket=body['ticket']       #pass ticket creation event containing work field
    issues=body['issues']       #pass array of issues 
    summary=ticket['work']['body']
    id=ticket['work']['id']
    ticketIssues=generateIssue(summary)
    print(ticketIssues)
    issueMap={}
    for ticketIssue in ticketIssues:
      for issue in issues:
        result=matchesIssue(issue['title'], ticketIssue)   #can be replaced with issue.body
        if(result == 'True'):
          if(issue['id'] not in issueMap):
            issueMap[issue['id']] = ticketIssue      #add issue if it matches an issue in the ticket

    return issueMap




