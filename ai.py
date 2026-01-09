from groq import Groq
from config import settings
import json

client = Groq(
    api_key=settings.GROQ_API_KEY,
)


def explain_code(code: str):
   
    system_prompt = (
        "You are a professional Senior Software Engineer. "
        "Your task is to analyze code and provide a structured technical review. "
        "You MUST return the output as a valid JSON object. "
        "Do not include any conversational text, markdown formatting, or 'json' code blocks."
    )

    
    user_prompt = f"Analyze this code and fill the following JSON schema:\n\n{code}"


    schema = {
        "heading": "A very short, clear title describing what the code does.",
        
        "summary": "A concise but clear explanation of the overall purpose and behavior of the code.",
        
        "logic_breakdown": [
            "Step-by-step explanation of the main logic in simple terms."
        ],
        
        "potential_issues": [
            "Possible bugs, edge cases, or scenarios where the code may fail or behave unexpectedly."
        ],
        
        "time_complexity": {
            "notation": "Big O time complexity (e.g., O(n), O(n^2))",
            "explanation": "Short explanation of why this time complexity applies."
        },
        
        "space_complexity": {
            "notation": "Big O space complexity",
            "explanation": "Short explanation of memory usage."
        },
        
        "improvements": [
            "Concrete suggestions to improve performance, readability, or maintainability."
        ],
    }


    try:
        chat_completion = client.chat.completions.create(
            messages=[
                {"role": "system", "content": system_prompt + f"\nSchema: {json.dumps(schema)}"},
                {"role": "user", "content": user_prompt}
            ],
            model="llama-3.3-70b-versatile",
            response_format={"type": "json_object"},
            temperature=0.2
        )

        return json.loads(chat_completion.choices[0].message.content)

    except Exception as e:
        print(f"Error parsing AI response: {e}")
        return {"error": "Failed to analyze code"}