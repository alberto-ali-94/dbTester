import asyncio
from tools.write_log import write_log
from CheeckyChan.main import Cheecky_Chan
from DoraExploradora.main import Dora_Exploradora


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
    ValidQuery, result = asyncio.run(Cheecky_Chan())

print("\n📦 Risultato finale salvato per ulteriori elaborazioni")
write_log(result)



print("🚀 Avvio Testarella!")
print("-"*30)