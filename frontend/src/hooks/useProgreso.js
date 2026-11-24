import { useEffect, useState } from "react";

const inicial = {
  xp: 0,
  racha: 0,
  vidas: 3,
  logros: [],
  estadisticas: { derivadas: 0, integrales: 0, vectores: 0, matrices: 0, optimizacion: 0, casos: { facil: 0, medio: 0, dificil: 0 } },
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
  const gastarXP = (cantidad = 10) => setProgreso((actual) => ({ ...actual, xp: Math.max(0, actual.xp - cantidad) }));
  const cerrarCaso = (dificultad, sinErrores = false, sinPistas = false) =>
    setProgreso((actual) => {
      const casos = { ...(actual.estadisticas.casos || { facil: 0, medio: 0, dificil: 0 }) };
      casos[dificultad] = (casos[dificultad] || 0) + 1;
      const logros = [...actual.logros];
      if (!logros.includes("Detective novato")) logros.push("Detective novato");
      if (!logros.includes("Caso cerrado")) logros.push("Caso cerrado");
      if (sinPistas && !logros.includes("Sin pistas")) logros.push("Sin pistas");
      return { ...actual, xp: actual.xp + 100, logros, estadisticas: { ...actual.estadisticas, casos } };
    });
  return { progreso, sumarAcierto, sumarError, reiniciar, gastarXP, cerrarCaso };
}
