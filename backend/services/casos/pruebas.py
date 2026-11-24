import math
import random
import sympy as sp


def _nuevo_random(seed):
    return random.Random(seed)


def enfriamiento(seed, dificultad):
    rng = _nuevo_random(f"{seed}-hora")
    ta = rng.randint(16, 24)
    k = rng.choice([0.055, 0.065, 0.075])
    hora_hallazgo = rng.randint(20, 23)
    t_esperado = rng.choice([2.0, 2.5, 3.0, 3.5])
    if dificultad == "dificil":
        t_esperado = rng.choice([2.25, 2.75, 3.25, 3.75])
    temperatura = ta + (37 - ta) * math.exp(-k * t_esperado)
    hora_muerte = hora_hallazgo - t_esperado
    datos = {
        "Ta": ta,
        "temperatura": round(temperatura, 2),
        "k": k,
        "hora_hallazgo": f"{hora_hallazgo}:00",
    }
    return datos, _hora_respuesta(hora_muerte), {
        "tipo": "derivada",
        "Ta": ta,
        "temperatura": round(temperatura, 2),
        "k": k,
        "t": round(t_esperado, 2),
    }


def _hora_respuesta(decimal):
    decimal = max(0, decimal)
    hora = int(decimal)
    minutos = round((decimal - hora) * 60)
    if minutos == 60:
        hora += 1
        minutos = 0
    return f"{hora}:{minutos:02d}"


def integrales(seed, dificultad):
    rng = _nuevo_random(f"{seed}-sangre")
    a = rng.randint(8, 16)
    k = rng.choice([0.18, 0.22, 0.28])
    t1 = rng.choice([0.0, 1.0, 2.0])
    t2 = t1 + rng.choice([2.0, 3.0, 4.0])
    t = sp.Symbol("t", positive=True)
    concentracion = sp.Float(a) * sp.exp(-k * t)
    dosis = sp.integrate(concentracion, (t, t1, t2)).evalf()
    letal = float(dosis) >= rng.choice([20.0, 25.0, 30.0])
    datos = {"A": a, "k": k, "t1": t1, "t2": t2, "umbral": 25.0}
    return datos, float(dosis), {
        "tipo": "integral",
        "datos": datos,
        "letal": letal,
        "x": [i / 2 for i in range(int(t1 * 2), int(t2 * 2) + 1)],
    }


def vectores(seed, dificultad):
    rng = _nuevo_random(f"{seed}-vector")
    is_3d = dificultad == "dificil"
    dimensions = 3 if is_3d else 2
    a = [rng.randint(-4, 4) for _ in range(dimensions)]
    d = [rng.randint(1, 5) for _ in range(dimensions)]
    b = [a[i] + d[i] for i in range(dimensions)]
    posiciones = [
        [b[i] + rng.randint(-3, 3) for i in range(dimensions)]
        for _ in range(4)
    ]
    correcta = rng.randrange(4)
    posiciones[correcta] = [a[i] + d[i] * rng.choice([0.25, 0.5, 0.75]) for i in range(dimensions)]
    am = sp.Matrix(a)
    dm = sp.Matrix(d)
    distancias = []
    for p in posiciones:
        pm = sp.Matrix(p)
        if dimensions == 2:
            distance = abs((pm - am)[0] * dm[1] - (pm - am)[1] * dm[0]) / dm.norm()
        else:
            distance = ((pm - am).cross(dm).norm() / dm.norm())
        distancias.append(float(distance))
    datos = {"A": a, "B": b, "posiciones": posiciones}
    return datos, correcta + 1, {
        "tipo": "vector",
        "datos": datos,
        "distancias": distancias,
    }


def hill(seed, dificultad):
    rng = _nuevo_random(f"{seed}-hill")
    if dificultad == "dificil":
        candidates = [
            sp.Matrix([[1, 2, 1], [0, 1, 1], [1, 1, 0]])
        ]
    else:
        candidates = [
            sp.Matrix([[3, 3], [2, 5]]),
            sp.Matrix([[5, 2], [1, 3]]),
            sp.Matrix([[3, 1], [2, 3]]),
        ]
    valid_matrices = [candidate for candidate in candidates if math.gcd(abs(int(candidate.det())), 26) == 1]
    if not valid_matrices:
        valid_matrices = [sp.Matrix([[3, 1], [2, 3]])]
    matrix = valid_matrices[rng.randrange(len(valid_matrices))]
    target = "LEY"
    if dificultad == "medio":
        target = "NORTE"
    if dificultad == "dificil":
        target = "CRIMINAL"
    numbers = [ord(ch) - 65 for ch in target]
    while len(numbers) % matrix.rows:
        numbers.append(23)
    cipher = []
    for i in range(0, len(numbers), matrix.rows):
        block = sp.Matrix(numbers[i:i + matrix.rows])
        cipher.extend((matrix * block).applyfunc(lambda x: x % 26))
    ciphered = "".join(chr(int(x) + 65) for x in cipher)
    inverse = matrix.inv_mod(26)
    data = {
        "matriz": [[int(value) for value in row] for row in matrix.tolist()],
        "cifrado": ciphered,
        "tamano": matrix.rows,
    }
    return data, target, {"tipo": "matriz", "matriz": matrix.tolist(), "respuesta": target}


def lagrange(seed, dificultad):
    rng = _nuevo_random(f"{seed}-lagrange")
    a, b = rng.randint(1, 4), rng.randint(1, 4)
    p, q = rng.randint(1, 3), rng.randint(1, 3)
    c = p * rng.randint(2, 5) + q * rng.randint(2, 5)
    x, y, lam = sp.symbols("x y lambda")
    objective = (x - a) ** 2 + (y - b) ** 2
    restriction = p * x + q * y - c
    equations = [
        sp.diff(objective, x) - lam * p,
        sp.diff(objective, y) - lam * q,
        restriction,
    ]
    solution = sp.solve(equations, (x, y, lam), dict=True)[0]
    punto = (float(solution[x]), float(solution[y]))
    dato = {"a": a, "b": b, "p": p, "q": q, "c": c}
    return dato, punto, {
        "tipo": "lagrange",
        "datos": dato,
        "punto": punto,
        "valor": float(objective.subs({x: solution[x], y: solution[y]})),
    }


PROOF_GENERATORS = {
    "hora": enfriamiento,
    "sangre": integrales,
    "vector": vectores,
    "hill": hill,
    "lagrange": lagrange,
}
