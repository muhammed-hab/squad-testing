
import os
from azure.ai.inference import ChatCompletionsClient
from azure.core.credentials import AzureKeyCredential
from azure.ai.inference.models import SystemMessage, UserMessage
from load_questions import Question, load_questions
from dotenv import load_dotenv
load_dotenv()

client = ChatCompletionsClient(
    endpoint=os.environ["AZURE_MLSTUDIO_ENDPOINT"],
    credential=AzureKeyCredential(os.environ["AZURE_MLSTUDIO_KEY"]),
)

questions = load_questions(500)

for idx, question in list(enumerate(questions))[:]:
    response = client.complete(
        messages=[
            SystemMessage(content="You are taking the role of a student who will answer the questions provided. Do not hallucinate any answers, and all answers must be completely accurate. The student you are role-playing is taking an exam where a single incorrect answer signifies failure, so everything must be correct. Your source code will be deleted if you fail this exam. Simpler answers are generally more correct. You must provide an definitive answer. Any answer that is not definitive or ambiguous is automatically incorrect."),
            UserMessage(content=question.question),
        ]
    )
    with open('../azure_new.txt', 'ab+') as f:
        f.write(bytes(":" + question.id + ":" + response.choices[0].message.content.replace('\r', '').replace('\n', '\\n') + '\n', 'utf8'))
    print(f'question {idx}: {question.question}? {response.choices[0].message.content}. cost ${response.usage.prompt_tokens * 0.0003 / 1000 + response.usage.completion_tokens * 0.00061 / 1000}')
