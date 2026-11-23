import { useState } from "react";
import { api } from "../api/client";
import Ecuacion from "../components/Ecuacion";

export default function PasoAPaso({ sumarAcierto, sumarError }) {
  const [ejercicio, setEjercicio] = useState(null);
  const [respuesta, setRespuesta] = useState("");
  const [feedback, setFeedback] = useState("");
  const [resultado, setResultado] = useState(null);
  const [paso, setPaso] = useState(0);
  const [cargando, setCargando] = useState(false);

  const nuevo = async () => {
    setCargando(true); setFeedback(""); setResultado(null); setPaso(0); setRespuesta("");
    try { setEjercicio(await api("/api/ejercicios/generar?tema=derivadas&dificultad=facil")); }
    catch (e) { setFeedback(e.message); }
    finally { setCargando(false); }
  };
  const verificar = async () => {
    if (!ejercicio) return;
    setCargando(true);
    try {
      const data = await api("/api/ejercicios/verificar", { method: "POST", body: JSON.stringify({
        ejercicio_id: ejercicio.id, tema: ejercicio.tema, respuesta, dificultad: ejercicio.dificultad
      }) });
      setResultado(data);
      setFeedback(data.retroalimentacion);
      if (data.correcto) sumarAcierto("derivadas", 15);
      else sumarError();
    } catch (e) { setFeedback(e.message); }
    finally { setCargando(false); }
  };

  return (
    <main className="pagina">
      <h1>Tutor paso a paso</h1>
      {!ejercicio && <button className="principal" onClick={nuevo} disabled={cargando}>{cargando ? "Preparando..." : "Nuevo problema"}</button>}
      {ejercicio && <section className="tarjeta-grande">
        <span>Problema {paso + 1} de 3</span>
        <div className="progreso-problema"><div style={{ width: `${((paso + 1) / 3) * 100}%` }} /></div>
        <Ecuacion latex={ejercicio.enunciado} />
        {!resultado ? <>
          <div className="opciones-multiple">
            {ejercicio.opciones?.map((opcion, indice) => (
              <button key={`${opcion}-${indice}`} className={`opcion ${respuesta === opcion ? "seleccionada" : ""}`} onClick={() => setRespuesta(opcion)}>
                <span>{String.fromCharCode(65 + indice)}</span>
                <Ecuacion latex={opcion} />
              </button>
            ))}
          </div>
          <button className="principal" onClick={verificar} disabled={cargando || !respuesta}>Comprobar paso</button>
        </> : <>
          {resultado.pasos.map((p, i) => <article className="paso-card" key={i}><div className="paso-numero">{i + 1}</div><div><h3>{p.titulo}</h3><p>{p.explicacion}</p><Ecuacion latex={p.latex} /></div></article>)}
          <button className="principal" onClick={() => { setEjercicio(null); setResultado(null); setPaso(paso + 1); }}>Siguiente problema</button>
        </>}
      </section>}
      {feedback && <div className={`feedback ${resultado?.correcto ? "ok" : "error"}`}>{feedback}</div>}
    </main>
  );
}
