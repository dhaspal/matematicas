import { Link } from "react-router-dom";
import { motion } from "framer-motion";
import { Swords, GraduationCap, FlaskConical, Crown } from "lucide-react";

const modos = [
  { to: "/duelo", titulo: "Duelo de Cartas", texto: "Resuelve ejercicios reales y derrota a la máquina.", icono: Swords, color: "violeta" },
  { to: "/paso", titulo: "Paso a Paso", texto: "Aprende derivadas e integrales con opciones guiadas.", icono: GraduationCap, color: "cian" },
  { to: "/laboratorio", titulo: "Laboratorio", texto: "Calculadora simbólica con pasos y gráficas.", icono: FlaskConical, color: "verde" },
  { to: "/jefe", titulo: "Jefe Final", texto: "Supera etapas combinadas de optimización.", icono: Crown, color: "dorado" },
];

export default function Inicio() {
  return (
    <main className="inicio">
      <section className="hero">
        <span className="badge">Calcula · Aprende · Conquista</span>
        <h1>Domina las matemáticas.<br /><em>Convierte números en poder.</em></h1>
      </section>
      <div className="modo-grid">
        {modos.map(({ to, titulo, texto, icono: Icono, color }) => (
          <motion.div key={to} whileHover={{ y: -6 }}>
            <Link className={`modo-card ${color}`} to={to}>
              <Icono size={32} />
              <h2>{titulo}</h2>
              <p>{texto}</p>
              <span>Entrar →</span>
            </Link>
          </motion.div>
        ))}
      </div>
    </main>
  );
}
