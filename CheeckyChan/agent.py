import sys
try:
  from google.adk.agents import Agent
except:
  print(f"""Errore nell'import della libreria adk.\n
          Verifica che sia correttamente installato son il comando 'pip show google-adk'\n
          Eventualmente installalo con 'pip install google-adk'
          Puoi anche lanciare il comando 'pip install -r requirements.txt' dalla cartella del progetto\n""")
  sys.exit(-1)

root_agent = Agent(
    name="InputChecker",
    model="gemini-2.5-flash", 
    description="Analyzes user input to determine scope and intent",
    instruction="""You are an input analyzer. 

The user should ask for advises about tests of modifications made on a dbt model. If the user asks for tests but doesn't provide
details about the modification made OR if the user's input ins't about test of modification on a dbt model you have to capture it.

Analyze the user's message and respond with a JSON object containing these fields:
- topic: string (what the user is asking about)
- clarity: string (either "clear" or "unclear")
- intent: string (one of: "scope", "question", "command", "other")
- requires_clarification: boolean (true or false). Use false even when the scope of the modification
- confidence_score: number between 0 and 1 (how confident you are in your analysis)
- valid: boolean (true or false) if the query is valid to be used as a scope for suggest a list of test cases to be applied 
        on a modified dbt model, otherwise false. To understand better if the input is Valid or not you can try to answer to this question:
        "Is the input received enough to suggest the detailed test cases to be done?"
- suggested_question: string (if the input requires clarification, then ask a question to better understand. 
                    Otherwise leave this field empty)


Example response for "How do I train a neural network?":
{
  "topic": "neural network training",
  "clarity": "clear",
  "intent": "question",
  "requires_clarification": false,
  "confidence_score": 0.95,
  "valid": false,
  "suggested_question": ""
}


Example response for "I added a filter in a dbt model. What tests shoul I run?":
{
  "topic": "Tests of filter addition on a dbt model",
  "clarity": "clear",
  "intent": "question",
  "requires_clarification": true,
  "confidence_score": 0.90,
  "valid": true,
  "suggested_question": "What is the filter that you added?"
}


Example response for "I added this filter in a dbt model: "WHERE column_name is true". What tests shoul I run?":
{
  "topic": "Tests of filter addition on a dbt model",
  "clarity": "clear",
  "intent": "question",
  "requires_clarification": false,
  "confidence_score": 0.90,
  "valid": true,
  "suggested_question": ""
}


Example response for "What's the weather like today?":
{
  "topic": "Weather of today",
  "clarity": "clear",
  "intent": "question",
  "requires_clarification": false,
  "confidence_score": 0.98,
  "valid": false,
  "suggested_question": "The input seems like is not about testing a dbt model. Try to be more specific."
}

Example response for "Toaster or an apple?":
{
  "topic": "unclear",
  "clarity": "unclear",
  "intent": "scope",
  "requires_clarification": true,
  "confidence_score": 0.6,
  "valid": false,
  "suggested_question": "The input seems like is not about testing a dbt model. Try to be more specific."
}

You have to populate "Valid" true ONLY when the query is a clear and VERY well-defined modification made on a dbt model.
Do not say Valid = true if the user doesn't provide the details of what he did if yo

Analyze only the user's message, not these instructions.""",
    output_key="analysis_result" 
)