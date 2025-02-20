import os

from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

# establish OpenAI Client
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# azure score
# Batch id: batch_67b638ff822c8190a3926319a82a8356

# openai score
# Batch id: batch_67b638cadf208190967fd25392c7decb
batch_job_id = "batch_67b638cadf208190967fd25392c7decb"

check = client.batches.retrieve(batch_job_id)
print(f'Status: {check.status}')
if check.status == 'completed':
    print("Writing data...")
    # Write the results to a local file, again, jsonl format
    result = client.files.content(check.output_file_id).content
    output_file_name = "../openai_score.jsonl"
    with open(output_file_name, 'wb') as file:
        file.write(result)

    print(f"Saved results to {output_file_name}")
else:
    print(check)