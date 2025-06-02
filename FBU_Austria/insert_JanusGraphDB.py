import csv
from gremlin_python.process.graph_traversal import __
from gremlin_python.process.anonymous_traversal import traversal
from gremlin_python.driver.driver_remote_connection import DriverRemoteConnection
from janusgraph_python.driver.serializer import JanusGraphSONSerializersV3d0
from tqdm import tqdm

connection = DriverRemoteConnection(
    'ws://localhost:8182/gremlin', 'g',
    message_serializer=JanusGraphSONSerializersV3d0()
)
g = traversal().withRemote(connection)

# Helper function: get or create vertex (avoids duplicates by indexed key)
def get_or_create_vertex(label, key, value, properties=None):
    vertex_traversal = g.V().has(label, key, value).fold().coalesce(
        __.unfold(),
        __.addV(label).property(key, value)
    )
    if properties:
        for k, v_prop in properties.items():
            vertex_traversal = vertex_traversal.property(k, v_prop)
    try:
        vertex = vertex_traversal.next()
    except StopIteration:
        print(f"Failed to create or get vertex: label={label}, key={key}, value={value}, properties={properties}")
        raise Exception("Failed to create or get vertex")
    return vertex.id

# Import companies, people, and addresses with deduplication
with open('../data/FBU_Testfaelle.csv', newline='', encoding='utf-8') as csvfile:
    reader = csv.DictReader(csvfile)
    for row in tqdm(reader):
        # Address as node (deduplicated)
        adresse_id = f"{row['Ort']}|{row['PLZ']}|{row['Straße']}"
        adresse_props = {'Ort': row['Ort'], 'PLZ': row['PLZ'], 'Straße': row['Straße']}
        adresse_v = g.V().has('Adresse', 'adresse_id', adresse_id) \
            .fold() \
            .coalesce(
                __.unfold(),
                __.addV('Adresse')
                .property('adresse_id', adresse_id)
                .property('Ort', row['Ort'])
                .property('PLZ', row['PLZ'])
                .property('Straße', row['Straße'])
            ).next()

        # Company as node (deduplicated)
        firma_props = {
            'Firmenname': row['Firmenname'],
            'FNR': row['FNR'],
            'Gewerbezweig': row['Gewerbezweig'],
            'Dummy_Eigenkapitalquote': float(row['Dummy_Eigenkapitalquote']),
            'Dummy_Bilanzsumme': float(row['Dummy_Bilanzsumme'])
        }
        firma_v = get_or_create_vertex('Firma', 'FNR', row['FNR'], firma_props)

        # Person as node (deduplicated)
        person_v = g.V().has('Person', 'Name', row['Name']) \
            .fold() \
            .coalesce(
                __.unfold(),
                __.addV('Person').property('Name', row['Name'])
            ).next()

        # Extract IDs
        firma_id = firma_v.id if hasattr(firma_v, 'id') else firma_v
        person_id = person_v.id if hasattr(person_v, 'id') else person_v
        adresse_id_vertex = adresse_v.id if hasattr(adresse_v, 'id') else adresse_v

        # Create edges
        g.V(person_id).addE('arbeitet_bei').to(__.V(firma_id)).property('Funktion', row['Funktion']).iterate()
        g.V(firma_id).addE('hat_adresse').to(__.V(adresse_id_vertex)).iterate()

# Import ownerships
with open('../data/beteiligungen.csv', newline='', encoding='utf-8') as csvfile:
    reader = csv.DictReader(csvfile)
    print("Import ownerships")
    for row in tqdm(reader):
        eigentuemer_list = g.V().has('Firma', 'FNR', row['Eigentümer_FNR']).toList()
        eigentuemer = eigentuemer_list[0] if eigentuemer_list else None

        ziel_list = g.V().has('Firma', 'FNR', row['Beteiligung_an_FNR']).toList()
        ziel = ziel_list[0] if ziel_list else None

        if eigentuemer and ziel:
            eigentuemer_id = eigentuemer.id if hasattr(eigentuemer, 'id') else eigentuemer
            ziel_id = ziel.id if hasattr(ziel, 'id') else ziel
            exists = g.V(eigentuemer_id).outE('beteiligt_an').where(__.inV().hasId(ziel_id)).toList()
            if not exists:
                g.V(eigentuemer_id).addE('beteiligt_an').to(__.V(ziel_id)).property('Prozent', int(row['Prozent'])).iterate()
        else:
            print(f"Fehlender Knoten für Beteiligung: Eigentümer_FNR={row['Eigentümer_FNR']}, Beteiligung_an_FNR={row['Beteiligung_an_FNR']}")

connection.close()
