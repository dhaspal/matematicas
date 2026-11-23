import { motion } from "framer-motion";

export default function Carta({ titulo, mundo, daño, onClick, deshabilitada }) {
  return (
    <motion.button whileHover={{ y: -8, scale: 1.03 }} whileTap={{ scale: 0.96 }}
      className="carta" onClick={onClick} disabled={deshabilitada}>
      <span className="mundo">{mundo}</span>
      <strong>{titulo}</strong>
      <span className="daño">{daño} daño</span>
    </motion.button>
  );
}
