from openai import OpenAI
from dotenv import load_dotenv
import os
import json

from load_azure_answers import load_azure_answers
from load_questions import load_questions

# load environmental variables
load_dotenv()

# System and user prompt to be filled in
system_prompt = "You are taking the role of a student who will answer the questions provided. Do not hallucinate any answers, and all answers must be completely accurate. The student you are role-playing is taking an exam where a single incorrect answer signifies failure, so everything must be correct. Your source code will be deleted if you fail this exam. Simpler answers are generally more correct. You must provide an definitive answer. Any answer that is not definitive or ambiguous is automatically incorrect."
user_prompt = "{question}"

input_batch_file = '../openai_ask_batch2.jsonl'
custom_id_gen = 'openai_ask_{id}'

questions = load_questions(500)

# this list will hold the individual tasks for each sample
tasks = []
for question in questions:
    # created our messages list. The system prompt has not custom fields, but the user prompt has to have emperor_name
    # filled with the current emperor
    messages = [{"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt.format(
                    question=question.question
                )}]

    # this is a custom id to keep track of each sample (IT MUST BE UNIQUE)
    custom_id = custom_id_gen.format(id=question.id)

    # this is the actual task to be performed. The response format is json_object, which means our prompt must contain
    # json instructions (as shown above in user prompt)
    task = {
        "custom_id": custom_id,
        "method": "POST",
        "url": "/v1/chat/completions",
        "body": {
            "model": "gpt-4o-mini",
            "messages": messages
        },
    }
    tasks.append(task)

# Here, we are writing a local file to store the tasks. This is a jsonl file, newline delimited)
with open(input_batch_file, 'w') as jfile:
    for task in tasks:
        jfile.write(json.dumps(task) + '\n')

# establish OpenAI Client
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# upload our batch file to OpenAI
batch_file = client.files.create(
    file=open(input_batch_file, 'rb'),
    purpose='batch'
)

# Run the batch using the completions endpoint
batch_job = client.batches.create(
  input_file_id=batch_file.id,
  endpoint="/v1/chat/completions",
  completion_window="24h"
)

print(f"Batch id: {batch_job.id}")
print(f"Batch object: {batch_job}")