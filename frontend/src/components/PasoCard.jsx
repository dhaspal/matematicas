import Ecuacion from "./Ecuacion";

export default function PasoCard({ paso, numero }) {
  return (
    <article className="paso-card">
      <div className="paso-numero">{numero}</div>
      <div>
        <h3>{paso.titulo}</h3>
        <p>{paso.explicacion}</p>
        {paso.latex && <Ecuacion latex={paso.latex} />}
        {paso.regla && <span className="etiqueta">{paso.regla}</span>}
      </div>
    </article>
  );
}
