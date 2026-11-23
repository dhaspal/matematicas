import { useState } from "react";
import { motion } from "framer-motion";
import { api } from "../api/client";
import Carta from "../components/Carta";
import Ecuacion from "../components/Ecuacion";

const cartas = [
  { titulo: "Derivar", mundo: "Derivadas", tema: "derivadas", daño: 10 },
  { titulo: "Integrar", mundo: "Integrales", tema: "integrales", daño: 20 },
  { titulo: "Producto punto", mundo: "Vectores", tema: "vectores", daño: 5 },
  { titulo: "Determinante", mundo: "Matrices", tema: "matrices", daño: 5 },
];

export default function DueloCartas({ sumarAcierto, sumarError }) {
  const [vidas, setVidas] = useState([100, 100]);
  const [turno, setTurno] = useState(1);
  const [ejercicio, setEjercicio] = useState(null);
  const [respuesta, setRespuesta] = useState("");
  const [feedback, setFeedback] = useState("");
  const [cartaActiva, setCartaActiva] = useState(null);
  const [ultimoDaño, setUltimoDaño] = useState(null);

  const jugar = async (carta) => {
    setCartaActiva(carta); setRespuesta(""); setFeedback("");
    try { setEjercicio(await api(`/api/ejercicios/generar?tema=${carta.tema}&dificultad=facil`)); }
    catch (e) { setFeedback(e.message); }
  };
  const resolver = async () => {
    if (!ejercicio || !respuesta) return;
    try {
      const data = await api("/api/ejercicios/verificar", { method: "POST", body: JSON.stringify({
        ejercicio_id: ejercicio.id, tema: ejercicio.tema, respuesta, dificultad: "facil"
      }) });
      setFeedback(data.retroalimentacion);
      if (data.correcto) {
        const daño = cartaActiva.daño;
        const rival = turno === 1 ? 1 : 0;
        setVidas((actuales) => {
          const siguiente = [...actuales];
          siguiente[rival] = Math.max(0, siguiente[rival] - daño);
          return siguiente;
        });
        setUltimoDaño({ jugador: turno, objetivo: rival + 1, cantidad: daño, tipo: "daño" });
        sumarAcierto(ejercicio.tema, daño);
        setFeedback(`¡Correcto! Jugador ${turno} inflige ${daño} de daño.`);
        setTurno((turno === 1 ? 2 : 1));
      } else {
        setUltimoDaño({ jugador: turno, objetivo: turno === 1 ? 2 : 1, cantidad: 0, tipo: "fallo" });
        sumarError();
        setFeedback(`Respuesta incorrecta. Pasa el turno al Jugador ${turno === 1 ? 2 : 1}.`);
        setTurno((turno === 1 ? 2 : 1));
      }
      setEjercicio(null);
    } catch (e) { setFeedback(e.message); }
  };

  return (
    <main className="pagina duelo">
      <h1>Duelo de cartas</h1>
      <div className="arena">
        <motion.div animate={ultimoDaño?.objetivo === 1 ? { x: [0, -12, 10, 0] } : {}} transition={{ duration: 0.35 }}
          className={turno === 1 ? "jugador activo" : "jugador"}>
          <div className="jugador-cabecera"><strong>Jugador 1</strong><span>{vidas[0]} HP</span></div>
          <div className="vida"><motion.div animate={{ width: `${vidas[0]}%` }} transition={{ duration: 0.5 }} /></div>
          {ultimoDaño?.objetivo === 1 && ultimoDaño.tipo === "daño" && <motion.div initial={{ y: 10, opacity: 0, scale: 0.7 }} animate={{ y: -18, opacity: 1, scale: 1 }} className="daño-flotante">-{ultimoDaño.cantidad} HP</motion.div>}
        </motion.div>
        <motion.div animate={{ scale: ejercicio ? [1, 1.08, 1] : 1 }} className="versus">VS</motion.div>
        <motion.div animate={ultimoDaño?.objetivo === 2 ? { x: [0, 12, -10, 0] } : {}} transition={{ duration: 0.35 }}
          className={turno === 2 ? "jugador activo" : "jugador"}>
          <div className="jugador-cabecera"><strong>Jugador 2</strong><span>{vidas[1]} HP</span></div>
          <div className="vida rival"><motion.div animate={{ width: `${vidas[1]}%` }} transition={{ duration: 0.5 }} /></div>
          {ultimoDaño?.objetivo === 2 && ultimoDaño.tipo === "daño" && <motion.div initial={{ y: 10, opacity: 0, scale: 0.7 }} animate={{ y: -18, opacity: 1, scale: 1 }} className="daño-flotante">-{ultimoDaño.cantidad} HP</motion.div>}
        </motion.div>
      </div>
      {vidas[1] === 0 && <div className="feedback ok">¡Victoria del Jugador 1!</div>}
      {vidas[0] === 0 && <div className="feedback ok">¡Victoria del Jugador 2!</div>}
      {vidas[0] > 0 && vidas[1] > 0 && <div className="turno">Turno del Jugador {turno}</div>}
      {ejercicio ? <section className="tarjeta-grande">
        <span className="badge">Jugador {turno} responde</span>
        <Ecuacion latex={ejercicio.enunciado} />
        <div className="opciones-multiple">
          {ejercicio.opciones?.map((opcion, indice) => (
            <button key={`${opcion}-${indice}`} className={`opcion ${respuesta === opcion ? "seleccionada" : ""}`} onClick={() => setRespuesta(opcion)}>
              <span>{String.fromCharCode(65 + indice)}</span>
              <Ecuacion latex={opcion} />
            </button>
          ))}
        </div>
        <button className="principal" onClick={resolver} disabled={!respuesta}>Responder y atacar</button>
      </section> : <div className="mano">{cartas.map((c) => <Carta key={c.titulo} {...c} onClick={() => jugar(c)} deshabilitada={vidas[0] === 0 || vidas[1] === 0} />)}</div>}
      {feedback && <div className="feedback">{feedback}</div>}
    </main>
  );
}
