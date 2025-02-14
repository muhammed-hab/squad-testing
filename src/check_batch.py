import os

from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

# establish OpenAI Client
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
# openai ask
# Batch id: batch_67ad30a960d48190b2524b07712e1d72
# Batch object: Batch(id='batch_67ad30a960d48190b2524b07712e1d72', completion_window='24h', created_at=1739403433, endpoint='/v1/chat/completions', input_file_id='file-5tmEKrE7M5oHNEHUgex49r', object='batch', status='validating', cancelled_at=None, cancelling_at=None, completed_at=None, error_file_id=None, errors=None, expired_at=None, expires_at=1739489833, failed_at=None, finalizing_at=None, in_progress_at=None, metadata=None, output_file_id=None, request_counts=BatchRequestCounts(completed=0, failed=0, total=0))

# azure check
# Batch id: batch_67ad3ef1b6ec8190b376f7fd75e40ff0
# Batch object: Batch(id='batch_67ad3ef1b6ec8190b376f7fd75e40ff0', completion_window='24h', created_at=1739407089, endpoint='/v1/chat/completions', input_file_id='file-LiAQsedjCRDsyWf7UER7ae', object='batch', status='validating', cancelled_at=None, cancelling_at=None, completed_at=None, error_file_id=None, errors=None, expired_at=None, expires_at=1739493489, failed_at=None, finalizing_at=None, in_progress_at=None, metadata=None, output_file_id=None, request_counts=BatchRequestCounts(completed=0, failed=0, total=0))
batch_job_id = "batch_67ad30a960d48190b2524b07712e1d72"

check = client.batches.retrieve(batch_job_id)
print(f'Status: {check.status}')
if check.status == 'expired':
    print("Writing data...")
    # Write the results to a local file, again, jsonl format
    result = client.files.content(check.output_file_id).content
    output_file_name = "openai_ask.jsonl"
    with open(output_file_name, 'wb') as file:
        file.write(result)

    print(f"Saved results to {output_file_name}")
else:
    print(check)