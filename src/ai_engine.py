from openai import OpenAI
from dotenv import load_dotenv
import os

load_dotenv()
api_key_env=os.getenv("OPENAI_API_KEY")

client = OpenAI(
    api_key=api_key_env
)


def Ai_answer(user_command: str) -> str:

    try:
        system_message = (
            "You are Nova, a smart, friendly virtual assistant like Alexa. "
            "Reply naturally based on the question. "
            "If the question is short, reply in 1 line. "
            "If it needs explanation, reply in 2-3 lines but keep it concise and useful."
        )

        completion = client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": system_message},
                {"role": "user", "content": user_command},
            ],
            temperature=0.7,
            max_tokens=150
        )

        response_text = completion.choices[0].message.content.strip()
        return response_text

    except Exception as e:
        error_msg = f"⚠️ Nova AI Error: {str(e)}"
        return error_msg

