import Plot from "react-plotly.js";

export default function Grafica({ datos }) {
  if (!datos) return null;
  if (datos.tipo === "derivada") {
    const expr = datos.funcion.replace("**", "^");
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
    const x = Array.from({ length: 100 }, (_, i) => -5 + i * 0.1);
    const y = x.map((v) => {
      try { return Function("x", `return ${datos.funcion.replaceAll("^", "**").replaceAll("**", "**")};`)(v); } catch { return 0; }
    });
    return <div className="grafica-contenedor"><Plot data={[{ x, y, type: "scatter", mode: "lines", fill: "tozeroy", line: { color: "#22d3ee" } }]} layout={{ autosize: true, height: 360, paper_bgcolor: "#111827", plot_bgcolor: "#111827", font: { color: "#e5e7eb" }, margin: { l: 55, r: 20, t: 30, b: 45 } }} config={{ responsive: true, displayModeBar: true, displaylogo: false }} /></div>;
  }
  if (datos.tipo === "vector") {
    const u = datos.u || [1, 1], v = datos.v || [0, 0];
    return <div className="grafica-contenedor"><Plot data={[{ x: [0, u[0]], y: [0, u[1]], mode: "lines+markers", name: "u", line: { color: "#8b5cf6" } }, { x: [0, v[0]], y: [0, v[1]], mode: "lines+markers", name: "v", line: { color: "#22d3ee" } }]} layout={{ autosize: true, height: 360, paper_bgcolor: "#111827", plot_bgcolor: "#111827", font: { color: "#e5e7eb" }, margin: { l: 55, r: 20, t: 30, b: 45 } }} config={{ responsive: true, displayModeBar: true, displaylogo: false }} /></div>;
  }
  return null;
}
