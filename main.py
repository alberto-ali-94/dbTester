import asyncio
import os
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.genai.types import Content, Part
from datetime import datetime
import json

# Import dell'agente dalla cartella InputChecker
from InputChecker.agent import root_agent as InputChecker 

async def main():
    APP_NAME = "input_analyzer_app"
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
    
    print(f"✅ Sessione creata: {session.id}")
    
    # Configura il runner
    runner = Runner(
        agent=InputChecker,
        app_name=APP_NAME,
        session_service=session_service
    )
    
    # Ottieni input dall'utente
    user_input = input("\n📝 Inserisci la tua query: ")
    
    print(f"\n🔍 Analisi in corso per: '{user_input}'")
    print("-" * 50)
    
    # Crea il contenuto del messaggio
    user_message = Content(
        role="user",
        parts=[Part(text=user_input)]
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
                        
            # Cattura i risultati delle tool calls
            if hasattr(event, 'tool_call_result'):
                tool_results.append(event.tool_call_result)
        
        # Mostra il risultato dell'analisi
        # print("\n📊 RISULTATO ANALISI:")
        # print("-" * 50)
        
        # if agent_response:
        #    full_response = "".join(agent_response)
        #    print(full_response)
        #else:
        #    print("⚠️  Nessuna risposta testuale ricevuta dall'agente")
        
        # Recupera lo stato aggiornato della sessione
        updated_session = await session_service.get_session(
            app_name=APP_NAME,
            user_id=USER_ID,
            session_id=session.id  # Usa session.id invece di SESSION_ID
        )
        
        print("\n💾 STATO SALVATO IN SESSIONE:")
        print("-" * 50)
        
        if updated_session.state:
            for key, value in updated_session.state.items():
                # Non stampare l'analysis_result qui per evitare duplicazione
                if key != 'analysis_result':
                    print(f"  • {key}: {value}")
                
            # L'output_key="analysis_result" nell'agente salva automaticamente la risposta
            if 'analysis_result' in updated_session.state:
                analysis_text = updated_session.state['analysis_result']
                
                try:
                    # Rimuovi i markdown code blocks se presenti
                    
                    
                    # Pulisci la risposta dai markdown code blocks
                    cleaned_text = analysis_text.strip()
                    
                    # Rimuovi ```json e ``` se presenti
                    if cleaned_text.startswith('```json'):
                        cleaned_text = cleaned_text[7:]  # Rimuovi ```json
                    elif cleaned_text.startswith('```'):
                        cleaned_text = cleaned_text[3:]  # Rimuovi ```
                    
                    if cleaned_text.endswith('```'):
                        cleaned_text = cleaned_text[:-3]  # Rimuovi ``` alla fine
                    
                    # Rimuovi spazi bianchi extra
                    # cleaned_text = cleaned_text.strip()
                    
                    # Parsa il JSON pulito
                    result = json.loads(cleaned_text)
                    
                    print(f"\n✅ Analisi completata con successo!")
                    print(f"   📌 Topic: {result.get('topic', 'N/A')}")
                    print(f"   🎯 Chiarezza: {result.get('clarity', 'N/A')}")
                    print(f"   🔍 Intent: {result.get('intent', 'N/A')}")
                    print(f"   ❓ Richiede chiarimenti: {result.get('requires_clarification', 'N/A')}")
                    print(f"   📊 Confidence: {result.get('confidence_score', 'N/A')}")
                    print(f"   ➡️  Valido: {result.get('valid', 'N/A')}")
                    
                    # Aggiungi timestamp al risultato
                    result['timestamp'] = datetime.now().isoformat()
                    
                    # ESEMPIO DI LOGICA BASATA SUI VALORI
                    print("\n🔄 ELABORAZIONE:")
                    print("-" * 50)
                    
                    # Logica basata su requires_clarification
                    if not(result.get('requires_clarification')) and result.get('valid') and (result.get('confidence_score', 0) > 0.8):
                        print("✅ La richiesta è chiara, posso procedere con l'elaborazione")
                        return True, result
                        
                    else:
                        print("⚠️  Sono necessari chiarimenti prima di procedere")
                        print(f"   Per favore chiarisci meglio cosa intendi per '{result.get('topic')}'")
                        return False, result
                    
                except json.JSONDecodeError as e:
                    # Secondo tentativo: prova a estrarre JSON con regex
                    try:
                        json_match = re.search(r'\{[^{}]*\}', analysis_text, re.DOTALL)
                        if json_match:
                            result = json.loads(json_match.group())
                            print(f"\n✅ Analisi completata (JSON estratto con regex)")
                            if not(result.get('requires_clarification')) and result.get('valid') and (result.get('confidence_score', 0) > 0.8):
                                print("✅ La richiesta è chiara, posso procedere con l'elaborazione")
                                return True, result
                        
                        else:
                            print("⚠️  Sono necessari chiarimenti prima di procedere")
                            print(f"   Per favore chiarisci meglio cosa intendi per '{result.get('topic')}'")
                            return False, result
                    except:
                        pass
                    
                    print(f"⚠️  Errore nel parsing del JSON: {e}")
                    print(f"   Risposta raw: {analysis_text[:200]}...")
                    return False, {'error': 'JSON parsing failed', 'raw_response': analysis_text}
        else:
            print("⚠️  Nessuno stato salvato nella sessione")
            
    except Exception as e:
        print(f"\n❌ Errore durante l'esecuzione: {e}")
        import traceback
        traceback.print_exc()
        return None



if __name__ == "__main__":
    # Verifica che la chiave API sia impostata
    if not os.getenv('GOOGLE_API_KEY'):
        print("❌ GOOGLE_API_KEY non impostata!")
        print("   Esegui: export GOOGLE_API_KEY='your-api-key'")
        exit(1)
    
    print("🚀 Avvio dell'analizzatore di input...")
    print("=" * 60)
    ValidQuery = False
    
    while(not(ValidQuery)):
        # Esegui una singola query
        ValidQuery, result = asyncio.run(main())
    

    
    if result:
        print("\n📦 Risultato finale disponibile per ulteriori elaborazioni:")
        print(result)