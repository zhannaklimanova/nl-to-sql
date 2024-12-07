import os
from dotenv import load_dotenv
from llm import LLM
from openai import OpenAI


class GPT4(LLM):
    def __init__(self):
        load_dotenv()
        self.api_key = os.getenv("OPENAI_API_KEY")
        self.client = OpenAI(api_key=self.api_key)
        self.client.files.create(
            file=open("NL2SQL/compact_schema_prompt.txt", "rb"), purpose="assistants"
        )
        self.system_instructions = "Generate SQL from the given schema and natural language prompt. Return it as a single line without any line breaks or newlines. Always end the query with a semicolon"
        self.assistant = self.client.beta.assistants.create(
            instructions=self.system_instructions
        )

    def nlq_to_sql(self, nlq: str) -> str:
        completion = self.client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": self.system_instructions},
                {
                    "role": "user",
                    "content": nlq,
                },
            ],
        )

        print(completion.choices[0].message)


if __name__ == "__main__":
    pass
