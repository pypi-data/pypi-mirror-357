import openai

client = openai.OpenAI(
    api_key="mbItpsZGYsE2cXqcwOIYys68TjyYUea9TUYVxR3q3olwqJvo1xmyJQQJ99BFACHYHv6XJ3w3AAAAACOGamcI",
    base_url="https://athir-mc2ko1av-eastus2.cognitiveservices.azure.com/openai/deployments/gpt-4.1",
    default_query={"api-version": "2024-12-01-preview"},
)

# Example using the deployment name
response = client.chat.completions.create(
    model="gpt-4.1",  # Replace with your deployment name
    messages=[
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": "Tell me a joke."},
    ]
)

print(response.choices[0].message.content)
