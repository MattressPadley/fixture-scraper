import os
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

api_key = os.getenv('OPENAI_API_KEY')
prompt = open('prompt.txt').read()

client = OpenAI()

assistant = client.beta.assistants.create(
    name='Fixture Scraper',
    instructions=prompt,
    tools=[{"type": "browsing"}]
    model='gpt-4o'
)

thread = client.beta.threads.create()

message = client.beta.threads.messages.create(
    thread_id=thread.id,
    role='user',
    content='Arri Skypanel s60c'
)

run = client.beta.threads.runs.create_and_poll(
    thread_id=thread.id,
    assistant_id=assistant.id,
    instructions=''
)

if run.status == 'completed':
    messages = client.beta.threads.messages.list(thread_id=thread.id)

    print