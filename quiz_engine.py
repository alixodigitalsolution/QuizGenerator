import google.generativeai as genai
import os
import json
import re
from dotenv import load_dotenv

# A professional pool of questions for when the API key is restricted
PROFESSIONAL_POOL = [
    {"question": "What is the primary objective of strategic planning in a professional environment?", "options": ["Increasing short-term profit", "Defining long-term goals and resources", "Reducing employee headcount", "Ignoring market trends"], "answer": 1, "explanation": "Strategic planning focus on aligning an organization's vision with its long-term capabilities and environmental opportunities."},
    {"question": "Which methodology emphasizes iterative development and customer feedback?", "options": ["Waterfall", "Agile", "Six Sigma", "Lean Manufacturing"], "answer": 1, "explanation": "Agile methodologies promote continuous improvement and rapid response to change through iterative cycles."},
    {"question": "In professional communication, what does 'Active Listening' involve?", "options": ["Waiting for your turn to speak", "Interrupting with better ideas", "Fully concentrating and responding to the speaker", "Recording the conversation for later"], "answer": 2, "explanation": "Active listening requires the listener to fully engage with, understand, and provide feedback to the speaker to ensure clear communication."},
    {"question": "What is 'Critical Thinking' in a decision-making context?", "options": ["Accepting information at face value", "The objective analysis and evaluation of an issue", "Making decisions based on intuition alone", "Following the most popular opinion"], "answer": 1, "explanation": "Critical thinking involves disciplined thinking that is clear, rational, and informed by evidence."},
    {"question": "How does 'Emotional Intelligence' benefit leadership?", "options": ["It allows leaders to ignore emotions", "It helps in controlling others", "It enables better self-awareness and empathy", "It prioritizes logic over people"], "answer": 2, "explanation": "Leaders with high EQ can better manage their own stress and understand the needs of their team, leading to higher morale."},
    {"question": "What is the role of 'Key Performance Indicators' (KPIs)?", "options": ["To track daily attendance", "To measure the success of an organization", "To replace employee feedback", "To increase project complexity"], "answer": 1, "explanation": "KPIs are quantifiable measures used to evaluate the success of an organization in reaching its performance targets."},
    {"question": "Which concept describes the advantage gained by producing in large quantities?", "options": ["Economies of Scale", "Law of Diminishing Returns", "Market Saturation", "Supply Chain Integration"], "answer": 0, "explanation": "Economies of scale are the cost advantages that enterprises obtain due to their scale of operation, with cost per unit of output decreasing with increasing scale."},
    {"question": "What defines a 'Growth Mindset'?", "options": ["Believing abilities are fixed", "Focusing only on the end result", "Believing abilities can be developed through dedication", "Avoiding challenges to prevent failure"], "answer": 2, "explanation": "A growth mindset thrives on challenge and sees failure not as evidence of unintelligence but as a heartening springboard for growth."},
    {"question": "What is 'Corporate Social Responsibility' (CSR)?", "options": ["Maximizing shareholder value only", "Reducing taxes through legal loopholes", "A business model that helps a company be socially accountable", "A marketing strategy for luxury goods"], "answer": 2, "explanation": "CSR initiatives are designed to improve society and the environment while maintaining a positive brand image."},
    {"question": "What is the purpose of 'Risk Management' in projects?", "options": ["To eliminate all uncertainty", "To identify, assess, and control threats", "To assign blame when things go wrong", "To increase the budget unnecessarily"], "answer": 1, "explanation": "Risk management involves anticipating potential issues and creating strategies to minimize their impact on project objectives."}
]

def get_demo_quiz(num=5, topic="General Knowledge"):
    """
    Returns the exact number of questions from the professional pool.
    """
    quiz = []
    for i in range(int(num)):
        # Cycle through the pool if num > pool size
        template = PROFESSIONAL_POOL[i % len(PROFESSIONAL_POOL)].copy()
        # Personalize the first question to mention the API issue
        if i == 0:
            template["question"] = f"🌟 [Pro Mode] Topic: {topic} | " + template["question"]
            template["explanation"] = "NOTE: Your API Key is currently restricted (403 Error). We are showing this professional sample quiz to demonstrate the engine's capabilities."
        quiz.append(template)
    return quiz

def get_model():
    load_dotenv()
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key: return None
    try:
        genai.configure(api_key=api_key)
        return genai.GenerativeModel(
            model_name="models/gemini-flash-latest",
            generation_config={"response_mime_type": "application/json", "max_output_tokens": 8192, "temperature": 0.7}
        )
    except: return None

def generate_quiz_from_text(text, num_questions=5, difficulty="Intermediate", quiz_type="Multiple Choice"):
    num_questions = int(num_questions)
    
    if text.lower().strip() == "demo":
        return get_demo_quiz(num_questions)

    model = get_model()
    if not model:
        return get_demo_quiz(num_questions, text)
    
    prompt = (
        f"Create a professional {quiz_type} quiz about: {text}. "
        f"Generate EXACTLY {num_questions} questions. "
        f"Difficulty Level: {difficulty}. "
        "Return the response ONLY as a JSON array of objects. "
        "Each object must have this EXACT schema: "
        '{"question": "string", "options": ["string", "string", "string", "string"], "answer": integer_index_0_to_3, "explanation": "string"}'
    )
    
    try:
        response = model.generate_content(prompt)
        raw_text = response.text
        
        # Clean markdown if present
        clean_json = re.sub(r'^```json\s*|\s*```$', '', raw_text.strip(), flags=re.MULTILINE)
        
        return json.loads(clean_json)
    except Exception as e:
        print(f"Generation error: {e}")
        return get_demo_quiz(num_questions, text)
