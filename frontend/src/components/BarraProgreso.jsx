import { Trophy, Flame, Heart, RotateCcw } from "lucide-react";

export default function BarraProgreso({ progreso, reiniciar }) {
  const nivel = Math.floor(progreso.xp / 100) + 1;
  const avance = progreso.xp % 100;
  return (
    <header className="barra">
      <div className="marca">MathQuest</div>
      <div className="stats">
        <span><Trophy size={17} /> Nivel {nivel}</span>
        <span><Flame size={17} /> Racha {progreso.racha}</span>
        <span><Heart size={17} /> {progreso.vidas} vidas</span>
        <span>{progreso.xp} XP</span>
      </div>
      <div className="barra-xp"><div style={{ width: `${avance}%` }} /></div>
      <button className="icono" onClick={reiniciar} title="Reiniciar progreso"><RotateCcw size={17} /></button>
    </header>
  );
}
