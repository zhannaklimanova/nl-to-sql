import os
from dotenv import load_dotenv
import google.generativeai as genai
from llm import LLM


class Gemini(LLM):
    def __init__(self):
        load_dotenv()
        self.api_key = os.getenv("GEMINI_API_KEY")
        genai.configure(api_key=self.api_key)
        self.model_name = "gemini-1.5-flash-8b"
        self.system_instruction = "Generate SQL from the given schema and natural language prompt. Return it as a single line without any line breaks or newlines. Always end the query with a semicolon"
        self.schema = genai.upload_file("compact_schema_prompt.txt")
        self.model = genai.GenerativeModel(
            model_name=self.model_name, system_instruction=self.system_instruction
        )

    def nlq_to_sql(self, nlq: str) -> str:
        return self.model.generate_content([nlq, self.schema]).text.strip()

if __name__ == "__main__":
    llm = Gemini()
    print(
        llm.nlq_to_sql("All Chants that have an 'a' but do not contain the phrase 'ad'")
    )
