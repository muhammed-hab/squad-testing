from dataclasses import dataclass

@dataclass
class AzureAnswer:
    questionId: str
    answer: str

def load_azure_answers(file: str) -> list[AzureAnswer]:
    with open(file, 'rb') as f:
        return [AzureAnswer(line.split(':',2)[1], line.split(':',2)[2]) for line in filter(lambda line: len(line) > 0 and not line.isspace(), str(f.read(), 'utf8').split('\n'))]

if __name__ == "__main__":
    for ans in load_azure_answers('../azure_new.txt'):
        print(ans)
