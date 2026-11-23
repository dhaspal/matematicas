import { useEffect, useState } from "react";

const inicial = {
  xp: 0,
  racha: 0,
  vidas: 3,
  logros: [],
  estadisticas: { derivadas: 0, integrales: 0, vectores: 0, matrices: 0, optimizacion: 0 },
};

export function useProgreso() {
  const [progreso, setProgreso] = useState(() => {
    try {
      return { ...inicial, ...JSON.parse(localStorage.getItem("mathquest-progreso")) };
    } catch {
      return inicial;
    }
  });

  useEffect(() => localStorage.setItem("mathquest-progreso", JSON.stringify(progreso)), [progreso]);

  const sumarAcierto = (mundo = "derivadas", puntos = 10) =>
    setProgreso((actual) => {
      const racha = actual.racha + 1;
      const logros = [...actual.logros];
      if (!logros.includes("Primera sangre")) logros.push("Primera sangre");
      if (racha >= 5 && !logros.includes("Racha de 5")) logros.push("Racha de 5");
      const clave = mundo === "optimizacion" ? "optimizacion" : mundo;
      return { ...actual, xp: actual.xp + puntos, racha, logros,
        estadisticas: { ...actual.estadisticas, [clave]: (actual.estadisticas[clave] || 0) + 1 } };
    });

  const sumarError = () => setProgreso((actual) => ({ ...actual, racha: 0, vidas: Math.max(0, actual.vidas - 1) }));
  const reiniciar = () => setProgreso(inicial);
  return { progreso, sumarAcierto, sumarError, reiniciar };
}
