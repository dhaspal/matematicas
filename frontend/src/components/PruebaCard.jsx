import { useState } from "react";
import Ecuacion from "./Ecuacion";
import PasoCard from "./PasoCard";
import Grafica from "./Grafica";

export default function PruebaCard({ prueba, onVerificar, cargando, feedback, resultado, onPista }) {
  const [respuesta, setRespuesta] = useState("");
  return (
    <section className="tarjeta-grande expediente-prueba">
      <span className="badge">PRUEBA {prueba.id.toUpperCase()}</span>
      <h2>{prueba.titulo}</h2>
      <p>{prueba.contexto}</p>
      <div className="datos-escena">
        {Object.entries(prueba.datos).map(([clave, valor]) => (
          <div key={clave}><small>{clave.replaceAll("_", " ")}</small><strong>{Array.isArray(valor) ? JSON.stringify(valor) : String(valor)}</strong></div>
        ))}
      </div>
      <h3>{prueba.pregunta}</h3>
      {!resultado?.correcta ? (
        <>
          <input className="respuesta-forense" value={respuesta} onChange={(event) => setRespuesta(event.target.value)} placeholder="Escribe tu respuesta" />
          <div className="acciones">
            <button className="principal" disabled={cargando || !respuesta.trim()} onClick={() => onVerificar(respuesta)}>Analizar evidencia</button>
            <button className="secundario" onClick={onPista}>Pista (-XP)</button>
          </div>
        </>
      ) : (
        <>
          {resultado.pasos.map((paso, indice) => <PasoCard key={indice} paso={paso} numero={indice + 1} />)}
          {resultado.grafica && <Grafica datos={resultado.grafica} />}
          <p className="feedback ok">{resultado.interpretacion}</p>
        </>
      )}
      {feedback && <div className={`feedback ${resultado?.correcta ? "ok" : "error"}`}>{feedback}</div>}
    </section>
  );
}
