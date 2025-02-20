import prompt
import os
from azure.ai.inference import ChatCompletionsClient
from azure.core.credentials import AzureKeyCredential
from azure.ai.inference.models import SystemMessage, UserMessage
from load_questions import Question, load_questions
from dotenv import load_dotenv

from src.RAGClient import RAGClient

load_dotenv()

client = ChatCompletionsClient(
    endpoint=os.environ["AZURE_MLSTUDIO_ENDPOINT"],
    credential=AzureKeyCredential(os.environ["AZURE_MLSTUDIO_KEY"]),
)

questions = load_questions(500)
rag = RAGClient(os.getenv("OPENAI_API_KEY"), 'rag.db')

for idx, question in list(enumerate(questions))[:]:
    response = client.complete(
        messages=[
            SystemMessage(content=prompt.system.format(context='\n'.join(rag.query(question.question, 5)))),
            UserMessage(content=prompt.user.format(question=question.question)),
        ]
    )
    with open('../azure_rag.txt', 'ab+') as f:
        f.write(bytes(":" + question.id + ":" + response.choices[0].message.content.replace('\r', '').replace('\n', '\\n') + '\n', 'utf8'))
    print(f'question {idx}: {question.question}? {response.choices[0].message.content}. cost ${response.usage.prompt_tokens * 0.0003 / 1000 + response.usage.completion_tokens * 0.00061 / 1000}')
