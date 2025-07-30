from ..config import gemini_api_key, github_pat
from google import genai
from openai import OpenAI

class AI:    
    @staticmethod
    # Gemini Text
    def Gemini(question):
        client = genai.Client(api_key=gemini_api_key)
        r = client.models.generate_content(
            model='gemini-2.0-flash-thinking-exp-01-21',
            contents= question
        )
        return r.text
    
    # Azure OpenAI GPT-4o Text
    @staticmethod
    def AzureOpenAI(question):            
        client = OpenAI(
            base_url = "https://models.inference.ai.azure.com",
            api_key = github_pat
        )
        r = client.chat.completions.create(
            messages=[
                {
                    "role": "user",
                    "content": question
                }
            ],
            temperature=1.0,
            top_p=1.0,
            max_tokens=4096,
            model="gpt-4o"
        )
        return r.choices[0].message.content
SelectAI = AI()