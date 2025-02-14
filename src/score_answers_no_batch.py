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
system_prompt = "You are a teacher tasked with determining whether a student’s answer to a question was correct, based on a set of possible correct answers. You must only use the provided possible correct answers to determine if the student's response was correct.\nYour response should only be a valid Json as shown below:\n{\"explanation\" (str): A short explanation of why the student's answer was correct or incorrect., \"score\" (bool): true if the student’s answer was correct, false if it was incorrect}"
user_prompt = "Question: {question}\n\nStudent's Response: {answer}\n\nPossible Correct Answers: {correct}\n\nYour Response:"

# answers = load_azure_answers('../azure_new.txt')
answers = load_gpt_answers('openai_ask.jsonl')

questions = {question.id:question for question in load_questions(500)}

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# this list will hold the individual tasks for each sample
for idx, ans in enumerate(answers):
    # created our messages list. The system prompt has not custom fields, but the user prompt has to have emperor_name
    # filled with the current emperor
    messages = [{"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt.format(
                    question=questions[ans.questionId].question,
                    answer=ans.answer,
                    correct='\n'.join(questions[ans.questionId].answers)
                )}]

    response = client.chat.completions.create(model='gpt-4o', messages=messages, response_format={
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
            })
    with open('openai_check.jsonl', 'ab+') as f:
        f.write(bytes(':' + ans.questionId + ':' + response.choices[0].message.content + '\n', 'utf8'))
    print(f'{idx} / {len(answers)} ' + ':' + ans.questionId + ':' + response.choices[0].message.content)
