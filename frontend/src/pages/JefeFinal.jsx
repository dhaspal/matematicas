import { useState } from "react";
import { api } from "../api/client";
import Ecuacion from "../components/Ecuacion";

export default function JefeFinal({ sumarAcierto, sumarError }) {
  const [jefe, setJefe] = useState(null);
  const [indice, setIndice] = useState(0);
  const [respuesta, setRespuesta] = useState("");
  const [vida, setVida] = useState(100);
  const [vidas, setVidas] = useState(3);
  const [mensaje, setMensaje] = useState("");

  const generar = async () => {
    setMensaje("");
    const data = await api("/api/jefe/generar");
    setJefe(data); setIndice(0); setVida(100); setVidas(3);
  };
  const verificar = async () => {
    if (!jefe) return;
    const etapa = jefe.etapas[indice];
    const data = await api("/api/jefe/verificar-etapa", { method: "POST", body: JSON.stringify({ respuesta, esperada: etapa.respuesta }) });
    setMensaje(data.mensaje);
    if (data.correcto) {
      setVida((v) => Math.max(0, v - 34));
      sumarAcierto("optimizacion", 25);
      setRespuesta("");
      setIndice((i) => i + 1);
    } else {
      setVidas((v) => Math.max(0, v - 1)); sumarError();
    }
  };
  const vencer = indice >= 3;
  return (
    <main className="pagina">
      <h1>Jefe Final: Restricciones</h1>
      {!jefe && <button className="principal" onClick={generar}>Invocar al jefe</button>}
      {jefe && <>
        <div className="jefe-datos"><div><strong>Vida del jefe</strong><div className="vida rival"><div style={{ width: `${vida}%` }} /></div></div><span>{vidas} vidas</span></div>
        <Ecuacion latex={`f(x,y)=${jefe.funcion},\\quad g(x,y)=${jefe.restriccion}=0`} />
        {vencer ? <div className="feedback ok">¡Jefe vencido! Logro: Jefe vencido.</div> : vidas === 0 ? <div className="feedback error">El jefe te derrotó. Genera otro desafío.</div> : <section className="tarjeta-grande">
          <h2>Etapa {indice + 1} de 3</h2><p>{jefe.etapas[indice].pregunta}</p>
          <div className="opciones-multiple">
            {jefe.etapas[indice].opciones.map((opcion, indiceOpcion) => (
              <button key={`${opcion.valor}-${indiceOpcion}`} className={`opcion ${respuesta === opcion.valor ? "seleccionada" : ""}`} onClick={() => setRespuesta(opcion.valor)}>
                <span>{String.fromCharCode(65 + indiceOpcion)}</span>
                <Ecuacion latex={opcion.latex} />
              </button>
            ))}
          </div>
          <div className="acciones"><button className="principal" onClick={verificar} disabled={!respuesta}>Responder</button><button className="secundario" onClick={() => setMensaje(jefe.etapas[indice].pista)}>Pista (-XP)</button></div>
        </section>}
      </>}
      {mensaje && <div className="feedback">{mensaje}</div>}
    </main>
  );
}
