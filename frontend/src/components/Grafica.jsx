import Plot from "react-plotly.js";

export default function Grafica({ datos }) {
  if (!datos) return null;
  if (datos.tipo === "derivada") {
    if (datos.k !== undefined) {
      const tMax = 8;
      const x = Array.from({ length: 81 }, (_, i) => i * tMax / 80);
      const y = x.map((t) => datos.Ta + (37 - datos.Ta) * Math.exp(-datos.k * t));
      return <div className="grafica-contenedor"><Plot data={[{ x, y, type: "scatter", mode: "lines", line: { color: "#f59e0b" } }]} layout={{ autosize: true, height: 360, paper_bgcolor: "#111827", plot_bgcolor: "#111827", font: { color: "#e5e7eb" }, margin: { l: 55, r: 20, t: 30, b: 45 } }} config={{ responsive: true, displayModeBar: true, displaylogo: false }} /></div>;
    }
    const expr = (datos.funcion || "0").replace("**", "^");
    const x = Array.from({ length: 121 }, (_, i) => -6 + i * 0.1);
    let y;
    try {
      y = x.map((v) => {
        const scope = expr.replaceAll("^", "**");
        return Function("x", `return ${scope};`)(v);
      });
    } catch {
      y = x.map(() => 0);
    }
    return <div className="grafica-contenedor"><Plot data={[{ x, y, type: "scatter", mode: "lines", line: { color: "#8b5cf6" } }]} layout={{ autosize: true, height: 360, paper_bgcolor: "#111827", plot_bgcolor: "#111827", font: { color: "#e5e7eb" }, margin: { l: 55, r: 20, t: 30, b: 45 } }} config={{ responsive: true, displayModeBar: true, displaylogo: false }} /></div>;
  }
  if (datos.tipo === "integral") {
    if (datos.datos) {
      const t1 = datos.datos.t1 ?? 0, t2 = datos.datos.t2 ?? 4;
      const x = Array.from({ length: 81 }, (_, i) => t1 + i * (t2 - t1) / 80);
      const y = x.map((t) => datos.datos.A * Math.exp(-datos.datos.k * t));
      return <div className="grafica-contenedor"><Plot data={[{ x, y, type: "scatter", mode: "lines", fill: "tozeroy", line: { color: "#22d3ee" } }]} layout={{ autosize: true, height: 360, paper_bgcolor: "#111827", plot_bgcolor: "#111827", font: { color: "#e5e7eb" }, margin: { l: 55, r: 20, t: 30, b: 45 } }} config={{ responsive: true, displayModeBar: true, displaylogo: false }} /></div>;
    }
    const x = Array.from({ length: 100 }, (_, i) => -5 + i * 0.1);
    const y = x.map((v) => {
      try { return Function("x", `return ${datos.funcion.replaceAll("^", "**").replaceAll("**", "**")};`)(v); } catch { return 0; }
    });
    return <div className="grafica-contenedor"><Plot data={[{ x, y, type: "scatter", mode: "lines", fill: "tozeroy", line: { color: "#22d3ee" } }]} layout={{ autosize: true, height: 360, paper_bgcolor: "#111827", plot_bgcolor: "#111827", font: { color: "#e5e7eb" }, margin: { l: 55, r: 20, t: 30, b: 45 } }} config={{ responsive: true, displayModeBar: true, displaylogo: false }} /></div>;
  }
  if (datos.tipo === "vector") {
    if (datos.datos) {
      const a = datos.datos.A || [0, 0], b = datos.datos.B || [1, 1];
      const posiciones = datos.datos.posiciones || [];
      return <div className="grafica-contenedor"><Plot
        data={[
          { x: [a[0], b[0]], y: [a[1], b[1]], mode: "lines+markers", name: "Trayectoria", line: { color: "#f59e0b", width: 4 } },
          ...posiciones.map((p, i) => ({ x: [p[0]], y: [p[1]], mode: "markers+text", text: [`P${i + 1}`], name: `P${i + 1}`, marker: { size: 12, color: i === (datos.distancias?.indexOf(Math.min(...datos.distancias)) || 0) ? "#22c55e" : "#ef4444" } })),
        ]}
        layout={{ autosize: true, height: 360, paper_bgcolor: "#111827", plot_bgcolor: "#111827", font: { color: "#e5e7eb" }, margin: { l: 55, r: 20, t: 30, b: 45 } }}
        config={{ responsive: true, displayModeBar: true, displaylogo: false }} /></div>;
    }
    const u = datos.u || [1, 1], v = datos.v || [0, 0];
    return <div className="grafica-contenedor"><Plot data={[{ x: [0, u[0]], y: [0, u[1]], mode: "lines+markers", name: "u", line: { color: "#8b5cf6" } }, { x: [0, v[0]], y: [0, v[1]], mode: "lines+markers", name: "v", line: { color: "#22d3ee" } }]} layout={{ autosize: true, height: 360, paper_bgcolor: "#111827", plot_bgcolor: "#111827", font: { color: "#e5e7eb" }, margin: { l: 55, r: 20, t: 30, b: 45 } }} config={{ responsive: true, displayModeBar: true, displaylogo: false }} /></div>;
  }
  if (datos.tipo === "integral") {
    const t1 = datos.datos?.t1 ?? 0, t2 = datos.datos?.t2 ?? 4;
    const x = Array.from({ length: 81 }, (_, i) => t1 + i * (t2 - t1) / 80);
    const y = x.map((v) => datos.datos?.A * Math.exp(-(datos.datos?.k || 0.2) * v));
    return <div className="grafica-contenedor"><Plot data={[{ x, y, type: "scatter", mode: "lines", fill: "tozeroy", line: { color: "#22d3ee" } }]} layout={{ autosize: true, height: 360, paper_bgcolor: "#111827", plot_bgcolor: "#111827", font: { color: "#e5e7eb" }, margin: { l: 55, r: 20, t: 30, b: 45 } }} config={{ responsive: true, displayModeBar: true, displaylogo: false }} /></div>;
  }
  if (datos.tipo === "lagrange") {
    const p = datos.datos || { p: 1, q: 1, c: 6, a: 2, b: 2 };
    const x = Array.from({ length: 41 }, (_, i) => -1 + i * 0.15);
    const y = x.map((v) => (p.c - p.p * v) / p.q);
    const punto = datos.punto || [0, 0];
    return <div className="grafica-contenedor"><Plot data={[{ x, y, type: "scatter", mode: "lines", name: "Restricción", line: { color: "#f59e0b" } }, { x: [punto[0]], y: [punto[1]], mode: "markers+text", text: ["Óptimo"], name: "Óptimo", marker: { color: "#22c55e", size: 13 } }]} layout={{ autosize: true, height: 360, paper_bgcolor: "#111827", plot_bgcolor: "#111827", font: { color: "#e5e7eb" }, margin: { l: 55, r: 20, t: 30, b: 45 } }} config={{ responsive: true, displayModeBar: true, displaylogo: false }} /></div>;
  }
  return null;
}
