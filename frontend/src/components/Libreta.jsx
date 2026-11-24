import Sospechoso from "./Sospechoso";

export default function Libreta({ sospechosos, descartados }) {
  return (
    <aside className="libreta">
      <div className="libreta-cabecera"><span>LIBRETA DEL DETECTIVE</span><b>EVIDENCIA</b></div>
      <div className="sospechosos-grid">
        {sospechosos.map((sospechoso) => (
          <Sospechoso key={sospechoso.id} sospechoso={sospechoso} descartado={descartados.includes(sospechoso.id)} />
        ))}
      </div>
    </aside>
  );
}
