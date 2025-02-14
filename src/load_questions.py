import json
from dataclasses import dataclass


@dataclass
class Question:
    question: str
    answers: list[str]
    context: str
    id: str

def load_questions(n: int) -> list[Question]:
    """
    Loads the first n questions from the squad dev v2 dataset, ignoring impossible questions
    :param n:
    :return:
    """
    with open('../dev-v2.0.json', 'rb') as f:
        dataset = json.load(f)

    result = []

    for topic in dataset['data']:
        for qset in topic['paragraphs']:
            context = qset['context']
            questions = qset['qas']
            for question in questions:
                if not question['is_impossible']:
                    result.append(
                        Question(
                            question['question'],
                            list(map(lambda ans: ans['text'], question['answers'])),
                            context,
                            question['id']
                        )
                    )
                if len(result) >= n:
                    return result

    return result
