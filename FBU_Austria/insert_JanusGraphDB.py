import csv
from gremlin_python.process.graph_traversal import __
from gremlin_python.process.anonymous_traversal import traversal
from gremlin_python.driver.driver_remote_connection import DriverRemoteConnection

# Verbindung zu JanusGraph
connection = DriverRemoteConnection('ws://localhost:8182/gremlin', 'g')
g = traversal().withRemote(connection)


# Hilfsfunktionen, um Duplikate zu vermeiden
def get_or_create_vertex(label, key, value, properties=None):
    vertex_traversal = g.addV(label).property(key, value)
    if properties:
        for k, v_prop in properties.items():
            vertex_traversal = vertex_traversal.property(k, v_prop)
    vertex = vertex_traversal.next()   # Executes the traversal and returns the vertex object
    return vertex.id

# Firmen, Personen und Adressen importieren
with open('../data/FBU_Testfaelle.csv', newline='', encoding='utf-8') as csvfile:
    reader = csv.DictReader(csvfile)
    for row in reader:
        # Adresse als Knoten
        adresse_id = f"{row['Ort']}|{row['PLZ']}|{row['Straße']}"
        adresse_props = {'Ort': row['Ort'], 'PLZ': row['PLZ'], 'Straße': row['Straße']}
        adresse_v = get_or_create_vertex('Adresse', 'adresse_id', adresse_id, adresse_props)

        # Firma als Knoten
        firma_props = {
            'Firmenname': row['Firmenname'],
            'FNR': row['FNR'],
            'Gewerbezweig': row['Gewerbezweig'],
            'Funktion': row['Funktion'],
            'Dummy_Eigenkapitalquote': float(row['Dummy_Eigenkapitalquote']),
            'Dummy_Bilanzsumme': float(row['Dummy_Bilanzsumme'])
        }
        firma_v = get_or_create_vertex('Firma', 'FNR', row['FNR'], firma_props)

        # Person als Knoten
        person_v = get_or_create_vertex('Person', 'Name', row['Name'])

        # IDs extrahieren
        firma_id = firma_v.id if hasattr(firma_v, 'id') else firma_v
        person_id = person_v.id if hasattr(person_v, 'id') else person_v
        adresse_id = adresse_v.id if hasattr(adresse_v, 'id') else adresse_v


        #g.V(person_id).addE('arbeitet_bei').to(__.V(firma_id)).iterate()

        # Firma hat Adresse (Edge)
        #g.V(firma_id).addE('hat_adresse').to(__.V(adresse_id)).iterate()

# Beteiligungen importieren
with open('data/beteiligungen.csv', newline='', encoding='utf-8') as csvfile:
    reader = csv.DictReader(csvfile)
    for row in reader:
        eigentuemer = g.V().has('Firma', 'FNR', row['Eigentümer_FNR']).tryNext().orElse(None)
        ziel = g.V().has('Firma', 'FNR', row['Beteiligung_an_FNR']).tryNext().orElse(None)
        if eigentuemer and ziel:
            eigentuemer_id = eigentuemer.id if hasattr(eigentuemer, 'id') else eigentuemer
            ziel_id = ziel.id if hasattr(ziel, 'id') else ziel
            # Prüfen, ob Kante schon existiert
            exists = g.V(eigentuemer_id).outE('beteiligt_an').where(__.inV().hasId(ziel_id)).toList()
            if not exists:
                g.V(eigentuemer_id).addE('beteiligt_an').to(__.V(ziel_id)).property('Prozent', int(row['Prozent'])).iterate()

connection.close()
