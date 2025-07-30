import openai

client = openai.OpenAI(
    api_key="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",
)

# Example using the deployment name
response = client.chat.completions.create(
    model="gpt-4o-mini",  # Replace with your deployment name
    messages=[
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": "Tell me a joke."},
    ]
)

print(response.choices[0].message.content)
