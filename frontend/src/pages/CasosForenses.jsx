import { useState } from "react";
import { motion } from "framer-motion";
import Libreta from "../components/Libreta";
import PruebaCard from "../components/PruebaCard";
import Sospechoso from "../components/Sospechoso";
import { casosApi } from "../api/casos";

export default function CasosForenses({ progreso, gastarXP, cerrarCaso, sumarAcierto, sumarError }) {
  const [dificultad, setDificultad] = useState("facil");
  const [seed, setSeed] = useState("");
  const [caso, setCaso] = useState(null);
  const [indice, setIndice] = useState(0);
  const [descartados, setDescartados] = useState([]);
  const [resultado, setResultado] = useState(null);
  const [feedback, setFeedback] = useState("");
  const [pistaTexto, setPistaTexto] = useState("");
  const [cargando, setCargando] = useState(false);
  const [acusacion, setAcusacion] = useState(false);
  const [seleccion, setSeleccion] = useState("");
  const [intentos, setIntentos] = useState(3);
  const [informe, setInforme] = useState(null);
  const [errores, setErrores] = useState(0);
  const [sinPistas, setSinPistas] = useState(true);

  const nuevoCaso = async () => {
    setCargando(true); setFeedback(""); setResultado(null); setPistaTexto("");
    try {
      const data = await casosApi.generar(dificultad, seed);
      setCaso(data); setSeed(data.seed); setIndice(0); setDescartados([]);
      setAcusacion(false); setSeleccion(""); setIntentos(3); setInforme(null); setErrores(0); setSinPistas(true);
    } catch (error) { setFeedback(error.message); }
    finally { setCargando(false); }
  };

  const verificar = async (respuesta) => {
    if (!caso) return;
    setCargando(true); setFeedback("");
    try {
      const data = await casosApi.verificar({ seed: caso.seed, dificultad, prueba_id: caso.pruebas[indice].id, respuesta });
      setResultado(data); setFeedback(data.retroalimentacion);
      if (data.correcta) {
        setDescartados((actual) => [...new Set([...actual, ...data.sospechosos_descartados])]);
        sumarAcierto?.("casos", 30);
      } else {
        setErrores((actual) => actual + 1);
        sumarError?.();
      }
    } catch (error) { setFeedback(error.message); }
    finally { setCargando(false); }
  };

  const pedirPista = async () => {
    if (!caso || progreso.xp < 10) return;
    try {
      const nivel = pistaTexto ? 2 : 1;
      const data = await casosApi.pista({ seed: caso.seed, dificultad, prueba_id: caso.pruebas[indice].id, nivel });
      setPistaTexto(data.pista); setSinPistas(false); gastarXP(10);
    } catch (error) { setFeedback(error.message); }
  };

  const siguiente = () => {
    setResultado(null); setFeedback(""); setPistaTexto("");
    if (indice + 1 < caso.pruebas.length) setIndice(indice + 1);
    else setAcusacion(true);
  };

  const acusar = async () => {
    if (!seleccion) return;
    setCargando(true);
    try {
      const data = await casosApi.acusar({ seed: caso.seed, dificultad, sospechoso_id: seleccion });
      setInforme(data);
      if (data.correcto) cerrarCaso(dificultad, errores === 0, sinPistas);
      else setIntentos((actual) => actual - 1);
    } catch (error) { setFeedback(error.message); }
    finally { setCargando(false); }
  };

  return (
    <main className="pagina casos-forenses">
      <motion.header initial={{ opacity: 0, y: -12 }} animate={{ opacity: 1, y: 0 }} className="casos-cabecera">
        <span className="casos-kicker">DIVISIÓN DE ANÁLISIS FORENSE</span>
        <h1>Casos Forenses</h1>
      </motion.header>
      {!caso && (
        <section className="tarjeta-grande configuracion-caso">
          <h2>Selecciona el expediente</h2>
          <div className="panel-controles">
            <label>Dificultad
              <select value={dificultad} onChange={(event) => setDificultad(event.target.value)}>
                <option value="facil">Fácil · 3 pruebas</option>
                <option value="medio">Medio · 4 pruebas</option>
                <option value="dificil">Difícil · 5 pruebas</option>
              </select>
            </label>
            <label>Seed opcional
              <input value={seed} onChange={(event) => setSeed(event.target.value)} placeholder="Ejemplo: 4512" />
            </label>
          </div>
          <button className="principal" disabled={cargando} onClick={nuevoCaso}>{cargando ? "Abriendo expediente..." : "Nuevo caso"}</button>
        </section>
      )}
      {caso && (
        <>
          <section className="historia-caso">
            <span>Expediente · {seed}</span>
            <h2>{caso.titulo}</h2>
            <p>{caso.historia}</p>
          </section>
          <div className="casos-layout">
            <Libreta sospechosos={caso.sospechosos} descartados={descartados} />
            <section className="casos-contenido">
              {!acusacion ? (
                <>
                  <div className="linea-pruebas">
                    {caso.pruebas.map((prueba, pruebaIndice) => (
                      <button key={prueba.id} className={pruebaIndice === indice ? "activa" : pruebaIndice < indice ? "resuelta" : ""}>
                        {pruebaIndice + 1}
                      </button>
                    ))}
                  </div>
                  <PruebaCard
                    prueba={caso.pruebas[indice]}
                    onVerificar={verificar}
                    cargando={cargando}
                    feedback={pistaTexto || feedback}
                    resultado={resultado}
                    onPista={pedirPista}
                  />
                  {resultado?.correcta && <button className="principal" onClick={siguiente}>{indice + 1 === caso.pruebas.length ? "Ir a la acusación" : "Siguiente prueba"}</button>}
                </>
              ) : (
                <section className="tarjeta-grande acusacion">
                  <h2>Acusación final</h2>
                  <p>Elige al único sospechoso compatible con todas las evidencias. Te quedan {intentos} oportunidades.</p>
                  <div className="acusacion-sospechosos">
                    {caso.sospechosos.map((sospechoso) => (
                      <button key={sospechoso.id} className={seleccion === sospechoso.id ? "seleccionado" : ""} onClick={() => setSeleccion(sospechoso.id)}>
                        {sospechoso.nombre}
                      </button>
                    ))}
                  </div>
                  <button className="principal" disabled={!seleccion || cargando || intentos === 0} onClick={acusar}>Presentar acusación</button>
                  {informe && <div className={`feedback ${informe.correcto ? "ok" : "error"}`}>
                    {informe.correcto ? informe.resumen_final : `${informe.resumen_final} Intentos restantes: ${intentos - (intentos > 0 ? 1 : 0)}.`}
                  </div>}
                  {informe?.correcto && <button className="secundario" onClick={() => setCaso(null)}>Abrir otro expediente</button>}
                  {intentos === 0 && <button className="secundario" onClick={() => setCaso(null)}>Reintentar con otro caso</button>}
                </section>
              )}
            </section>
          </div>
        </>
      )}
      {feedback && !caso && <div className="feedback error">{feedback}</div>}
    </main>
  );
}
