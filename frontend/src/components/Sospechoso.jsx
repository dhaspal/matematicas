import { motion } from "framer-motion";

export default function Sospechoso({ sospechoso, descartado }) {
  return (
    <motion.article
      layout
      animate={{ opacity: descartado ? 0.42 : 1, scale: descartado ? 0.96 : 1 }}
      className={`sospechoso ${descartado ? "descartado" : ""}`}
    >
      <span className="expediente-codigo">{sospechoso.id.toUpperCase()}</span>
      <h3>{sospechoso.nombre}</h3>
      <p>{sospechoso.coartada}</p>
      {descartado && <strong>DESCARTADO</strong>}
    </motion.article>
  );
}
