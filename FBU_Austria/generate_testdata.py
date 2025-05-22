import pandas as pd
import random

num_rows = 1000

firmenname = [f"Firma_{i}" for i in range(1, num_rows+1)]
fnr = [f"FNR_{random.randint(1000, 9999)}" for _ in range(num_rows)]
staat = [random.choice(["Österreich"]) for _ in range(num_rows)]
orte = [random.choice(["Linz", "Wien", "Salzburg", "Redlham", "Gmunden", "Amstetten", "Guntramsdorf"]) for _ in range(num_rows)]
plz = [str(random.randint(10000, 99999)) for _ in range(num_rows)]
strasse = [f"Straße_{random.randint(1, 100)}" for _ in range(num_rows)]
gewerbezweig = [random.choice(["IT", "Handel", "Produktion", "Dienstleistung", "Finanzen"]) for _ in range(num_rows)]
funktion = [random.choice(["Geschäftsführer"]) for _ in range(num_rows)]
name = [f"Name_{i}" for i in range(1, num_rows+1)]

def generate_dummy_eigenkapitalquote():
    return round(random.uniform(0.1, 0.6), 2)

def generate_dummy_bilanzsumme():
    return round(random.uniform(1e6, 1e8), 2)

dummy_eigenkapitalquote = [generate_dummy_eigenkapitalquote() for _ in range(num_rows)]
dummy_bilanzsumme = [generate_dummy_bilanzsumme() for _ in range(num_rows)]


# Eigentumsstruktur generieren (mit FNR)
beteiligungen = []

for target_idx, target_fnr in enumerate(fnr):
    # Mit 50% Wahrscheinlichkeit erhält eine Firma Beteiligungen
    if random.random() < 0.7:
        continue
    # Anzahl der Eigentümer (1 bis 3)
    num_owners = random.randint(1, 3)
    # Verfügbare Eigentümer (nicht sich selbst)
    possible_owners = [f for i, f in enumerate(fnr) if i != target_idx]
    if len(possible_owners) == 0:
        continue
    owners = random.sample(possible_owners, min(num_owners, len(possible_owners)))
    # Beteiligungsprozente generieren, die zusammen <= 100% ergeben
    remaining = 100
    percentages = []
    for i in range(len(owners)):
        if i == len(owners) - 1:
            pct = remaining
        else:
            pct = random.randint(5, min(60, remaining - 5 * (len(owners) - i - 1)))
        percentages.append(pct)
        remaining -= pct
        if remaining <= 0:
            break
    # Beteiligungen speichern
    for owner_fnr, pct in zip(owners, percentages):
        if pct > 0:
            beteiligungen.append({
                "Eigentümer_FNR": owner_fnr,
                "Beteiligung_an_FNR": target_fnr,
                "Prozent": pct
            })

df = pd.DataFrame({
    "Firmenname": firmenname,
    "FNR": fnr,
    "Staat": staat,
    "Ort": orte,
    "PLZ": plz,
    "Straße": strasse,
    "Gewerbezweig": gewerbezweig,
    "Funktion": funktion,
    "Name": name,
    "Dummy_Eigenkapitalquote": dummy_eigenkapitalquote,
    "Dummy_Bilanzsumme": dummy_bilanzsumme
})

csv_filename = "data/FBU_Testfaelle.csv"
df.to_csv(csv_filename, index=False)

# Speichern der Beteiligungsstruktur
beteiligungen_df = pd.DataFrame(beteiligungen)
beteiligungen_df.to_csv("beteiligungen.csv", index=False)
