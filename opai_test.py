from openai import OpenAI
import os

filename = "/Users/shuhangge/Desktop/my_projects/pdfprocess/test.pdf"
prompt = "Extract the content from the file provided without altering it. Just output its exact content and nothing else."

client = OpenAI(api_key=os.environ.get("MY_OPENAI_KEY"))

file = client.files.create(
    file=open(filename, "rb"),
    purpose="user_data"
)

response = client.responses.create(
    model="gpt-4.1",
    input=[
        {
            "role": "user",
            "content": [
                {
                    "type": "input_file",
                    "file_id": file.id,
                },
                {
                    "type": "input_text",
                    "text": prompt,
                },
            ]
        }
    ]
)
print(response)
'''Response(id='resp_681eb25c06ac81919dbe456deb4345260a9ed9361667bac0', 
created_at=1746842204.0, error=None, incomplete_details=None, instructions=None, metadata={}, 
model='gpt-4.1-2025-04-14', object='response', 
output=[ResponseOutputMessage(id='msg_681eb25d70e881919dd4ddc8779801e10a9ed9361667bac0', 
content=[ResponseOutputText(annotations=[], 
text='This is a simple test PDF\nTesting PDF extraction', type='output_text')], 
role='assistant', status='completed', type='message')], 
parallel_tool_calls=True, temperature=1.0, tool_choice='auto', 
tools=[], top_p=1.0, max_output_tokens=None, previous_response_id=None, 
reasoning=Reasoning(effort=None, generate_summary=None, summary=None), 
service_tier='default', status='completed', 
text=ResponseTextConfig(format=ResponseFormatText(type='text')), 
truncation='disabled', 
usage=ResponseUsage(input_tokens=53, input_tokens_details=InputTokensDetails(cached_tokens=0), 
output_tokens=11, output_tokens_details=OutputTokensDetails(reasoning_tokens=0), total_tokens=64), 
user=None, store=True)'''