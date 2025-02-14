import json
from dataclasses import dataclass


@dataclass
class GPTAnswer:
    questionId: str
    answer: str

def load_gpt_answers(file: str) -> list[GPTAnswer]:
    with open(file, 'rb') as f:
        return [GPTAnswer(resp['custom_id'][11:], resp['response']['body']['choices'][0]['message']['content']) for resp in [json.loads(line) for line in
                filter(lambda line: len(line) > 0 and not line.isspace(), str(f.read(), 'utf8').split('\n'))]]

if __name__ == "__main__":
    for ans in load_gpt_answers('openai_ask.jsonl'):
        print(ans)
