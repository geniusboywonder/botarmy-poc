from openai import OpenAI

# Initialize the OpenAI client with your API key
client = OpenAI(api_key='')

try:
    # Make a simple test request to the API
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": "Hello, is this working?"}],
        max_tokens=10
    )
    print("API Key is working! Response:", response.choices[0].message.content)
except Exception as e:
    print("Error:", str(e))
