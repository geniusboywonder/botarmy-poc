import os
from openai import OpenAI

<<<<<<< HEAD
# Initialize the OpenAI client with your API key
client = OpenAI(api_key='')
=======
# Retrieve the API key from Replit's environment variables
api_key = os.getenv('OPENAI_API_KEY')

# Initialize the OpenAI client with the API key
client = OpenAI(api_key=api_key)
>>>>>>> 14c40d8 (completed HITL and agent messaging)

try:
    # Make a simple test request to the API
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": "Hello, is this working?"}],
        max_tokens=10
    )
    print("API Key is working! Response:", response.choices[0].message.content)
except Exception as e:
    print("Error:", str(e)
