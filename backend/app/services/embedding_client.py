import os
from dotenv import load_dotenv
from openai import OpenAI

EMBED_MODEL = "text-embedding-3-small"
CHAT_MODEL = "gpt-4o-mini"

# 1) Load the .env file
load_dotenv()

# 2) Read the variable
api_key = os.getenv("OPENAI_API_KEY")

# Debug check (optional)
if not api_key:
    raise ValueError("OPENAI_API_KEY not found in environment!")

# 3) Initialize OpenAI client
client = OpenAI(api_key=api_key)

def get_embedding(text: str):
    resp = client.embeddings.create(
        model=EMBED_MODEL,
        input=text
    )
    return resp.data[0].embedding

def get_text_response(prompt: str):
    response = client.chat.completions.create(
        model=CHAT_MODEL,
        messages=[
            {"role": "user", "content": prompt}
        ]
    )
    return response.choices[0].message.content