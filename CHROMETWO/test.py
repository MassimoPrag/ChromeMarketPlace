from openai import OpenAI
client = "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"

response = client.responses.create(
    model="gpt-4o",
    input="Write a one-sentence bedtime story about a unicorn."
)

print(response.output_text)