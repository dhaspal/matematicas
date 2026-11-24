# MathQuest

MathQuest es una plataforma educativa en español para practicar cálculo y álgebra lineal con ejercicios y cálculos reales de SymPy.

## Requisitos

- Python 3.11 o superior
- Node.js 18 o superior

## Ejecutar el backend

```powershell
cd mathquest\backend
python -m pip install -r requirements.txt
python -m uvicorn main:app --reload --host 127.0.0.1 --port 8000
```

Verifica el estado en `http://127.0.0.1:8000/api/salud`.

## Ejecutar el frontend

```powershell
cd mathquest\frontend
npm install
npm run dev
```

Abre `http://localhost:5173`.

## Modos disponibles

- **Duelo de Cartas:** ejercicios por mundo y combate contra la máquina.
- **Paso a Paso:** tutor con ejercicios y soluciones reveladas paso a paso.
- **Laboratorio:** derivadas, integrales, vectores, matrices y Lagrange con expresiones de SymPy.
- **Jefe Final:** etapas combinadas de optimización.

## Ejemplos de prueba

- Derivada: `x^2`
- Integral: `3*x^2`
- Integral definida: `x^2` entre 0 y 2
- Vector suma: u `[2,3]`, v `[1,-1]`
- Matriz determinante:
  ```text
  [[1,2],[3,4]]
  ```
- Lagrange: función `x^2+y^2`, restricción `x+y-4`

## Cómo presentar el proyecto

Demostración sugerida de 3 minutos:

1. Inicia en **Laboratorio** y calcula la derivada de `x^2` para mostrar el resultado simbólico y los pasos.
2. Después abre **Paso a Paso**, genera un ejercicio de derivadas y muestra la respuesta aceptada simbólicamente.
3. Continúa con **Duelo de Cartas** y resuelve una carta en vivo.
4. Cierra con **Jefe Final** para mostrar las etapas encadenadas.

## Casos Forenses: la matemática real detrás de cada prueba

**Casos Forenses** convierte derivadas, integrales, vectores, matrices y optimización en evidencia investigativa:

- **Ley de enfriamiento:** estima la hora de fallecimiento en medicina forense.
- **Farmacocinética:** integra una concentración exponencial para medir una dosis acumulada.
- **Balística:** calcula la distancia de posiciones a una trayectoria y reconstruye el origen del disparo.
- **Cifrado de Hill:** usa matrices, determinantes e inversos modulares para descifrar mensajes.
- **Lagrange:** optimiza rutas o puntos con restricciones lineales.

Casos Forenses funciona como una calculadora matemática aplicada:

1. Selecciona una aplicación: enfriamiento, concentración, vectores, Hill o Lagrange.
2. Modifica los datos de entrada.
3. Pulsa **Calcular y explicar**.
4. Consulta el resultado, la gráfica y los pasos obtenidos con SymPy.
