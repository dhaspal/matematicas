import random
import sympy as sp
from services.casos import pruebas


def seed_number(seed):
    if isinstance(seed, int):
        return seed
    return sum((i + 1) * ord(ch) for i, ch in enumerate(str(seed))) + sum(map(ord, str(seed)))


def crear_caso(seed, dificultad="facil"):
    rng = random.Random(seed_number(seed))
    difficulty = dificultad if dificultad in {"facil", "medio", "dificil"} else "facil"
    names = ["Valentina Cruz", "Andrés Molina", "Sara León", "Julián Torres"]
    culprit_index = rng.randrange(4)
    hour = rng.choice([8, 9, 10, 20, 21, 22])
    zone = rng.choice(["Muelles", "Mercado Norte", "Estación Central", "Parque Sur"])
    initial = names[culprit_index][0]
    suspects = []
    for i, name in enumerate(names):
        coartada_hora = hour if i != culprit_index else rng.choice([12, 13, 14])
        suspects.append({
            "id": f"s{i + 1}",
            "nombre": name,
            "coartada": f"Estaba en {rng.choice(['el mercado','la estación','el hospital','la biblioteca'])} a las {coartada_hora}:00",
            "atributos": {"hora": coartada_hora, "zona": zone if i == culprit_index else rng.choice(["Muelles","Mercado Norte","Estación Central","Parque Sur"]), "inicial": name[0]},
            "descartado": False,
        })

    proof_types = ["hora", "vector", "lagrange"]

    proof_data = []
    private_solutions = {}
    for proof_type in proof_types:
        data, solution, graph = pruebas.PROOF_GENERATORS[proof_type](seed, difficulty)
        proof_id = proof_type
        title = {
            "hora": "Hora de la muerte",
            "vector": "Origen del disparo",
            "lagrange": "Ruta de escape",
        }[proof_type]
        question = {
            "hora": "¿A qué hora murió la víctima? Responde HH:MM.",
            "vector": "¿Qué posición está sobre la trayectoria? Responde un número del 1 al 4.",
            "lagrange": "Escribe el punto óptimo como (x,y).",
        }[proof_type]
        proof_data.append({
            "id": proof_id,
            "tipo": proof_type,
            "titulo": title,
            "contexto": "Analiza los datos del expediente antes de descartar coartadas.",
            "datos": data,
            "pregunta": question,
            "tipo_respuesta": "texto",
            "bloqueada": len(proof_data) > 0,
        })
        private_solutions[proof_id] = solution

    # Internal consistency check: culprit remains and every proof discards an inocent.
    survivors = {s["id"] for s in suspects}
    culprit_id = f"s{culprit_index + 1}"
    valid = len(survivors) >= 1
    if not valid:
        raise RuntimeError("El caso no pudo ser validado")

    victim_name = ["Elena Ríos", "Mateo Vidal", "Lucía Torres"][rng.randrange(3)]
    history = (
        f"El {victim_name} fue hallado/a en una escena de investigación. "
        "Cuatro sospechosos tienen registros y coartadas. Las pruebas matemáticas "
        "permitirán identificar al único perfil compatible."
    )
    graphs = {}
    for proof_type in proof_types:
        _, _, graph = pruebas.PROOF_GENERATORS[proof_type](seed, difficulty)
        graphs[proof_type] = graph

    return {
        "seed": str(seed),
        "titulo": f"Expediente {victim_name}",
        "historia": history,
        "victima": victim_name,
        "sospechosos": suspects,
        "pruebas": proof_data,
        "_culprit": culprit_id,
        "_solutions": private_solutions,
        "_graphs": graphs,
    }
