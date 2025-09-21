import logging
logging.getLogger('google_genai.types').setLevel(logging.ERROR)
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.genai.types import Content, Part
import sys
import os
import json
import write_log


from agent import root_agent as TestAdvisor 
from datetime import datetime



async def Testarella(model_id:str,user_query:str):
    # Verifica che la chiave API sia impostata
    if not os.getenv('GOOGLE_API_KEY'):
        print("❌ GOOGLE_API_KEY non impostata!")
        print("   Esegui: export GOOGLE_API_KEY='your-api-key'")
        sys.exit(1)

    APP_NAME = "testarella"
    USER_ID = "test_user"
    SESSION_ID = "session_123"
    
    # Inizializza il servizio di sessione
    session_service = InMemorySessionService()
    
    # Crea la sessione
    session = await session_service.create_session(
        app_name=APP_NAME,
        user_id=USER_ID,
        session_id=SESSION_ID
    )
    print("🤖 [Testarella]: 🔄 ELABORAZIONE IN CORSO")
    #print(f"🤖 [Testarella]: ✅ Sessione creata: {session.id}")
    
    # Configura il runner
    runner = Runner(
        agent=TestAdvisor,
        app_name=APP_NAME,
        session_service=session_service
    )
    
    
    # Crea il contenuto del messaggio
    user_message = Content(
        role="user",
        parts=[Part(text=f"MODEL_ID: {model_id}, USER_QUERY: {user_query}")]
    )
    
    try:
        # Variabili per raccogliere il risultato
        agent_response = []
        tool_results = []
        
        # Esegui l'agente - usa session.id invece di SESSION_ID
        async for event in runner.run_async(
            user_id=USER_ID,
            session_id=session.id,  # Usa l'ID della sessione appena creata
            new_message=user_message
        ):
            # Gestisci diversi tipi di eventi
            if hasattr(event, 'content') and event.content and event.content.parts:
                for part in event.content.parts:
                    if hasattr(part, 'text') and part.text:
                        agent_response.append(part.text)
                    elif hasattr(part, 'function_call'):
                        pass  # Ignora function calls
                    elif hasattr(part, 'function_response'):
                        pass  # Ignora function responses  
                    elif hasattr(part,'thought_signature'):
                        pass #ignore thought_signature
                    # Cattura i risultati delle tool calls
                    if hasattr(event, 'tool_call_result'):
                        tool_results.append(event.tool_call_result)
        
        # Recupera lo stato aggiornato della sessione
        updated_session = await session_service.get_session(
            app_name=APP_NAME,
            user_id=USER_ID,
            session_id=session.id  
        )
        
        
        if updated_session.state:                
            # L'output_key="analysis_result" nell'agente salva automaticamente la risposta
            if 'analysis_result' in updated_session.state:
                analysis_text = updated_session.state['analysis_result']
                
                try:
                    # Pulisci la risposta dai markdown code blocks
                    cleaned_text = analysis_text.strip()
                    
                    # Rimuovi ```json e ``` se presenti
                    if cleaned_text.startswith('```json'):
                        cleaned_text = cleaned_text[7:]  # Rimuovi ```json
                    elif cleaned_text.startswith('```'):
                        cleaned_text = cleaned_text[3:]  # Rimuovi ```
                    
                    if cleaned_text.endswith('```'):
                        cleaned_text = cleaned_text[:-3]  # Rimuovi ``` alla fine
                    
                    # Parsa il JSON pulito
                    result = json.loads(cleaned_text)
                    
                    write_log.write_log(result,"testarella")
                    print("🤖 [Testarella] Analisi completata e salvata su file")
                    return result

                
                    
                except:
                    pass
                    
                    print(f"   ⚠️ Errore nel parsing del JSON: {e}")
                    print(f"   Risposta raw: {analysis_text[:200]}...")
                    return None
        else:
            print("   ⚠️ Nessuno stato salvato nella sessione")
            
    except Exception as e:
        print(f"\n❌ Errore durante l'esecuzione: {e}")
        import traceback
        traceback.print_exc()
        return None

