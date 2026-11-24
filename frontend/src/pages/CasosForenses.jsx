import { useState } from "react";
import { motion } from "framer-motion";
import Ecuacion from "../components/Ecuacion";
import Grafica from "../components/Grafica";
import PasoCard from "../components/PasoCard";
import { casosApi } from "../api/casos";

const aplicaciones = [
  { id: "hora", nombre: "Hora de la muerte", subtitulo: "Ley de enfriamiento de Newton", formulas: "T(t)=T_a+(37-T_a)e^{-kt}" },
  { id: "vector", nombre: "Origen del disparo", subtitulo: "Reconstrucción balística", formulas: "d(P,r)=|(P-A)\\times d|/|d|" },
  { id: "lagrange", nombre: "Ruta de escape", subtitulo: "Optimización con restricciones", formulas: "\\nabla f=\\lambda\\nabla g" },
];

const iniciales = {
  hora: { Ta: 20, temperatura: 34.61, k: 0.055, hora_hallazgo: "20:00" },
  vector: { A: [4, 3], B: [9, 8], posiciones: [[7, 7], [4, 3], [9, 8]] },
  lagrange: { a: 3, b: 3, p: 3, q: 2, c: 18 },
};

function listaATexto(valor) {
  return JSON.stringify(valor);
}

export default function CasosForenses() {
  const [activa, setActiva] = useState("hora");
  const [datos, setDatos] = useState(iniciales);
  const [resultado, setResultado] = useState(null);
  const [cargando, setCargando] = useState(false);
  const [error, setError] = useState("");

  const cambiarDato = (clave, valor) => {
    setDatos((actual) => ({ ...actual, [activa]: { ...actual[activa], [clave]: valor } }));
  };

  const cambiarCoordenada = (grupo, indice, eje, valor) => {
    setDatos((actual) => {
      const actualVector = { ...actual.vector };
      if (grupo === "A" || grupo === "B") {
        const punto = [...actualVector[grupo]];
        punto[eje] = valor === "" ? "" : Number(valor);
        actualVector[grupo] = punto;
      } else {
        const posiciones = actualVector.posiciones.map((punto) => [...punto]);
        posiciones[indice][eje] = valor === "" ? "" : Number(valor);
        actualVector.posiciones = posiciones;
      }
      return { ...actual, vector: actualVector };
    });
  };

  const agregarPosicion = () => {
    setDatos((actual) => ({
      ...actual,
      vector: {
        ...actual.vector,
        posiciones: [...actual.vector.posiciones, [0, 0]],
      },
    }));
  };

  const quitarPosicion = (indice) => {
    setDatos((actual) => ({
      ...actual,
      vector: {
        ...actual.vector,
        posiciones: actual.vector.posiciones.filter((_, i) => i !== indice),
      },
    }));
  };

  const calcular = async () => {
    setCargando(true); setError(""); setResultado(null);
    try {
      let entrada = datos[activa];
      if (activa === "vector" && typeof entrada.A === "string") {
        entrada = { ...entrada, A: JSON.parse(entrada.A), B: JSON.parse(entrada.B), posiciones: JSON.parse(entrada.posiciones) };
      }
      const data = await casosApi.calcular(activa, entrada);
      setResultado(data);
    } catch (e) {
      setError(e.message);
    } finally {
      setCargando(false);
    }
  };

  const cambiarAplicacion = (id) => {
    setActiva(id); setResultado(null); setError("");
  };

  const campos = (prueba) => {
    const actual = datos[prueba];
    if (prueba === "hora") return [
      ["Ta", "Temperatura ambiente", "T_a", actual.Ta],
      ["temperatura", "Temperatura medida del cuerpo", "T(t)", actual.temperatura],
      ["k", "Constante de enfriamiento", "k", actual.k],
      ["hora_hallazgo", "Hora del hallazgo", "t_h", actual.hora_hallazgo],
    ];
    return [
      ["a", "Centro de la distancia en X", "a", actual.a],
      ["b", "Centro de la distancia en Y", "b", actual.b],
      ["p", "Coeficiente de la ruta en X", "p", actual.p],
      ["q", "Coeficiente de la ruta en Y", "q", actual.q],
      ["c", "Constante de la restricción", "c", actual.c],
    ];
  };

  const actualAplicacion = aplicaciones.find((item) => item.id === activa);
  const utilidad = {
    hora: "Estima desde cuándo llevaba enfriándose el cuerpo. El resultado sirve como intervalo aproximado de fallecimiento.",
    vector: "Indica cuál de las posiciones candidatas está sobre la trayectoria y aproxima su ubicación como norte, sur, noreste, suroeste, etc.",
    lagrange: "Encuentra el punto óptimo sobre una ruta o restricción lineal y aproxima hacia qué cuadrante queda.",
  }[activa];
  return (
    <main className="pagina casos-forenses">
      <header className="casos-cabecera">
        <span className="casos-kicker">MATEMÁTICA APLICADA</span>
        <h1>Casos Forenses</h1>
        <p>Introduce datos reales y observa cómo las matemáticas ayudan a resolver situaciones prácticas.</p>
      </header>

      <nav className="casos-aplicaciones" aria-label="Aplicaciones matemáticas">
        {aplicaciones.map((item) => (
          <button key={item.id} className={activa === item.id ? "activa" : ""} onClick={() => cambiarAplicacion(item.id)}>
            <strong>{item.nombre}</strong><span>{item.subtitulo}</span>
          </button>
        ))}
      </nav>

      <section className="casos-calculadora">
        <div className="casos-formulario">
          <span className="casos-kicker">DATOS DE ENTRADA</span>
          <h2>{actualAplicacion.nombre}</h2>
          <Ecuacion latex={actualAplicacion.formulas} />
          {activa === "vector" ? (
            <div className="coordenadas-vector">
              <section>
                <h3>Primer punto de impacto</h3>
                <div className="coordenadas-fila">
                  <label>Distancia horizontal (X)<input type="number" value={datos.vector.A[0]} onChange={(e) => cambiarCoordenada("A", 0, 0, e.target.value)} /></label>
                  <label>Distancia vertical (Y)<input type="number" value={datos.vector.A[1]} onChange={(e) => cambiarCoordenada("A", 0, 1, e.target.value)} /></label>
                </div>
              </section>
              <section>
                <h3>Segundo punto de impacto</h3>
                <div className="coordenadas-fila">
                  <label>Distancia horizontal (X)<input type="number" value={datos.vector.B[0]} onChange={(e) => cambiarCoordenada("B", 0, 0, e.target.value)} /></label>
                  <label>Distancia vertical (Y)<input type="number" value={datos.vector.B[1]} onChange={(e) => cambiarCoordenada("B", 0, 1, e.target.value)} /></label>
                </div>
              </section>
              <section className="posiciones-candidatas">
                <div className="posiciones-cabecera"><h3>Posibles ubicaciones</h3><button type="button" onClick={agregarPosicion}>Agregar ubicación</button></div>
                {datos.vector.posiciones.map((posicion, indice) => (
                  <div className="posicion-fila" key={indice}>
                    <span>Ubicación {indice + 1}</span>
                    <label>Este-oeste (X)<input type="number" value={posicion[0]} onChange={(e) => cambiarCoordenada("P", indice, 0, e.target.value)} /></label>
                    <label>Norte-sur (Y)<input type="number" value={posicion[1]} onChange={(e) => cambiarCoordenada("P", indice, 1, e.target.value)} /></label>
                    {datos.vector.posiciones.length > 2 && <button type="button" className="quitar-posicion" onClick={() => quitarPosicion(indice)} aria-label={`Eliminar ubicación ${indice + 1}`}>Eliminar</button>}
                  </div>
                ))}
              </section>
            </div>
          ) : campos(activa).map(([clave, etiqueta, variable, valor]) => (
            <label className="campo-forense" key={clave}>
              <strong>{etiqueta}</strong>
              <span className="variable-forense"><Ecuacion latex={variable} /></span>
              <input
                value={valor}
                onChange={(event) => {
                  const lista = activa === "vector";
                  if (lista || (activa === "hora" && clave === "hora_hallazgo")) cambiarDato(clave, event.target.value);
                  else cambiarDato(clave, event.target.value === "" ? "" : Number(event.target.value));
                }}
              />
            </label>
          ))}
          <button className="principal" disabled={cargando} onClick={calcular}>{cargando ? "Calculando..." : "Calcular y explicar"}</button>
          {error && <div className="feedback error">{error}</div>}
        </div>

        <div className="casos-resultado">
          {!resultado ? (
            <div className="resultado-vacio">
              <strong>Resultado</strong>
              <p>Completa los datos y calcula para ver la utilidad práctica y los pasos.</p>
            </div>
          ) : (
            <motion.div initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }}>
              <div className="resultado-final forense">
                <h2>Resultado</h2>
                <strong>{resultado.resultado}</strong>
                {resultado.horas_transcurridas !== undefined && (
                  <p>
                    Han transcurrido aproximadamente <strong>{resultado.horas_transcurridas} horas</strong>.
                    La temperatura cambia alrededor de <strong>{resultado.derivada} °C/h</strong> en ese momento.
                  </p>
                )}
                {resultado.letal !== undefined && <p>{resultado.letal ? "Supera el umbral de referencia." : "Está por debajo del umbral de referencia."}</p>}
                {resultado.distancias && (
                  <p>
                    Posición compatible: P{resultado.resultado}. Menor distancia a la trayectoria.
                    <strong> Dirección aproximada: {resultado.cuadrante}</strong>
                  </p>
                )}
                {resultado.cuadrante && activa === "lagrange" && (
                  <p>Ruta de escape aproximada: <strong>{resultado.cuadrante}</strong>. {resultado.direccion}</p>
                )}
                <p className="resultado-utilidad">{utilidad}</p>
              </div>
              {resultado.grafica && <Grafica datos={resultado.grafica} />}
              <h2>Cómo se calcula</h2>
              <div className="pasos-lista">
                {resultado.pasos.map((paso, indice) => <PasoCard key={indice} paso={paso} numero={indice + 1} />)}
              </div>
            </motion.div>
          )}
        </div>
      </section>
    </main>
  );
}
