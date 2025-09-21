import asyncio
from tools.write_log import write_log
from CheeckyChan.main import Cheecky_Chan
from DoraExploradora.main import Dora_Exploradora
from Testarella.main import Testarella


dbt_model = input ("📝 Inserisci il modello dbt che hai modificato:")
print("🚀 Avvio Dora Exploradora!")
print("-"*30)
ValidModel = False
while (not(ValidModel)):
    ValidModel, lineage = Dora_Exploradora(dbt_model)


print("🚀 Avvio Cheecky Chan!")
print("-"*30)
ValidQuery = False

while(not(ValidQuery)):
    ValidQuery, analysis_result, user_query = asyncio.run(Cheecky_Chan())

write_log(analysis_result,"CheeckyChan")
print("  -> 📦 Risultato finale salvato per ulteriori verifiche")




print("🚀 Avvio Testarella!")
print("-"*30)
tests = asyncio.run(Testarella(dbt_model,user_query))

