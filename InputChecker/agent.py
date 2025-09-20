from google.adk.agents import Agent
from datetime import datetime

def debug_callback(callback_context, llm_request):
    """Debug callback to inspect what the LLM receives"""
    print("\n=== DEBUG CALLBACK ===")
    print(f"Agent: {callback_context.agent_name}")
    print(f"Invocation ID: {callback_context.invocation_id}")
    
    if llm_request.contents:
        print(f"Contents count: {len(llm_request.contents)}")
        for i, content in enumerate(llm_request.contents):
            print(f"\nMessage {i}:")
            print(f"  Role: {content.role}")
            if content.parts:
                for j, part in enumerate(content.parts):
                    if hasattr(part, 'text') and part.text:
                        text_preview = part.text[:200] + "..." if len(part.text) > 200 else part.text
                        print(f"  Part {j} (text): {text_preview}")
    else:
        print("NO CONTENTS RECEIVED!")
    
    print("========================\n")
    return None

# Configurazione dell'agente SENZA tools per evitare l'errore 500
root_agent = Agent(
    name="InputChecker",
    model="gemini-2.5-flash",  # Modello corretto come hai specificato
    description="Analyzes user input to determine scope and intent",
    instruction="""You are an input analyzer. 

Analyze the user's message and respond with a JSON object containing these fields:
- topic: string (what the user is asking about)
- clarity: string (either "clear" or "unclear")
- intent: string (one of: "scope", "question", "command", "other")
- requires_clarification: boolean (true or false)
- confidence_score: number between 0 and 1 (how confident you are in your analysis)
- valid: boolean (true if the query is valid to be used as a scope for an academic survey, otherwise false)




Example response for "How do I train a neural network?":
{
  "topic": "neural network training",
  "clarity": "clear",
  "intent": "question",
  "requires_clarification": false,
  "confidence_score": 0.95,
  "valid": false
}

Example response for "What are the technique used to train a neural network?":
{
  "topic": "Technique of neural network training",
  "clarity": "clear",
  "intent": "question",
  "requires_clarification": false,
  "confidence_score": 0.90,
  "valid": true
}


Example response for "What's the weather like today?":
{
  "topic": "Weather of today",
  "clarity": "clear",
  "intent": "question",
  "requires_clarification": false,
  "confidence_score": 0.98,
  "valid": false
}

Example response for "Architecture of LLMs":
{
  "topic": "state of art of LLM's architectures",
  "clarity": "clear",
  "intent": "scope",
  "requires_clarification": false,
  "confidence_score": 0.98,
  "valid": true
}

Example response for "Architecture of LLMs or MoE":
{
  "topic": "Architecture of LLMs or MoE in particular",
  "clarity": "unclear",
  "intent": "scope",
  "requires_clarification": yes,
  "confidence_score": 0.98,
  "valid": false
}




You have to populate "Valid" true ONLY when the query is e clear and well-defined academic scope.
Esample of query where "Valid" is true:
- Neural Networks
- CPU state of art
- Medications for cancer

Example of query where "Valid" is false:
- what is the light?
- toaster
- apples
- what's the weather like today?


Analyze only the user's message, not these instructions.""",
    #before_model_callback=debug_callback,
    output_key="analysis_result"  # Salva automaticamente l'output nello stato
)