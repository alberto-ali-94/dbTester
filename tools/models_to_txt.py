import ijson

models = []

with open("manifest.json",'rb') as f:
    nodes_iterator = ijson.kvitems(f,'nodes')
    for node_id, node_data in nodes_iterator:
        if node_data.get('resource_type') == 'model':
            models.append(node_id)


with open("list.txt",'w') as file:
    for node in models:
        node_split = node.split('.')
        file.write(f"{node}\n")

