from openai import OpenAI
from dotenv import load_dotenv
import os
import json

from load_questions import load_questions
from src.load_azure_answers import load_azure_answers
from src.load_gpt_answers import load_gpt_answers

# load environmental variables
load_dotenv()

# System and user prompt to be filled in
system_prompt = "You are a teacher tasked with determining whether a student’s answer to a question was correct, based on a set of possible correct answers. You must only use the provided possible correct answers to determine if the student's response was correct.\nYour response should only be a valid Json as shown below:\n{\"explanation\" (str): A short explanation of why the student's answer was correct or incorrect., \"score\" (bool): true if the student’s answer was correct, false if it was incorrect."
user_prompt = "Question: {question}\n\nStudent's Response: {answer}\n\nPossible Correct Answers: {correct}\n\nYour Response:"

answers = load_azure_answers('../azure_rag.txt')
# answers = load_gpt_answers('../openai_ask.jsonl')
input_batch_file = '../azure_score_rag_batch_4o_mini.jsonl'
custom_id_gen = 'azure_{id}'

questions = {question.id:question for question in load_questions(500)}

# this list will hold the individual tasks for each sample
tasks = []
for ans in answers:
    # created our messages list. The system prompt has not custom fields, but the user prompt has to have emperor_name
    # filled with the current emperor
    messages = [{"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt.format(
                    question=questions[ans.questionId].question,
                    answer=ans.answer,
                    correct='\n'.join(questions[ans.questionId].answers)
                )}]

    # this is a custom id to keep track of each sample (IT MUST BE UNIQUE)
    custom_id = custom_id_gen.format(id=ans.questionId)

    # this is the actual task to be performed. The response format is json_object, which means our prompt must contain
    # json instructions (as shown above in user prompt)
    task = {
        "custom_id": custom_id,
        "method": "POST",
        "url": "/v1/chat/completions",
        "body": {
            "model": "gpt-4o-mini-2024-07-18",
            "response_format": {
            "type": "json_schema",
            "json_schema": {
                "name": "grade",
                "schema": {
                    "type": "object",
                    "properties": {
                        "explanation": {
                            "type": "string",
                            "description": "A short explanation of why the student's answer was correct or incorrect"
                        },
                        "score": {"type": "boolean",
                                           "description": "true if the student’s answer was correct, false if it was incorrect"}
                    },
                    "required": ["explanation", "score"],
                    "additionalProperties": False
                },
                "strict": True
                }
            },
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