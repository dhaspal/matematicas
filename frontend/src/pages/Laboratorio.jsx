import { useRef, useState } from "react";
import { api } from "../api/client";
import Ecuacion from "../components/Ecuacion";
import Grafica from "../components/Grafica";
import PasoCard from "../components/PasoCard";
import EditorMatriz from "../components/EditorMatriz";

const ejemplos = [
  { nombre: "Derivar x²", tipo: "derivada", entrada: { funcion: "x^2" } },
  { nombre: "Integral de 3x²", tipo: "integral", entrada: { funcion: "3*x^2" } },
  { nombre: "Vector suma", tipo: "vector", entrada: { operacion: "suma", u: [2, 3], v: [1, -1] } },
];

export default function Laboratorio() {
  const [tipo, setTipo] = useState("derivada");
  const [funcion, setFuncion] = useState("x^2");
  const [operacion, setOperacion] = useState("suma");
  const [u, setU] = useState("[2,3]");
  const [v, setV] = useState("[1,-1]");
  const [matriz, setMatriz] = useState([[1, 2], [3, 4]]);
  const [resultado, setResultado] = useState(null);
  const [cargando, setCargando] = useState(false);
  const [error, setError] = useState("");
  const entradaRef = useRef(null);

  const insertar = (texto) => {
    const entrada = entradaRef.current;
    if (!entrada) {
      setFuncion((actual) => actual + texto);
      return;
    }
    const inicio = entrada.selectionStart ?? funcion.length;
    const fin = entrada.selectionEnd ?? inicio;
    const siguiente = funcion.slice(0, inicio) + texto + funcion.slice(fin);
    setFuncion(siguiente);
    requestAnimationFrame(() => {
      entrada.focus();
      entrada.setSelectionRange(inicio + texto.length, inicio + texto.length);
    });
  };

  const borrar = () => {
    const entrada = entradaRef.current;
    if (!entrada) {
      setFuncion((actual) => actual.slice(0, -1));
      return;
    }
    const inicio = entrada.selectionStart ?? funcion.length;
    const fin = entrada.selectionEnd ?? inicio;
    if (inicio !== fin) {
      setFuncion(funcion.slice(0, inicio) + funcion.slice(fin));
      requestAnimationFrame(() => { entrada.focus(); entrada.setSelectionRange(inicio, inicio); });
    } else if (inicio > 0) {
      setFuncion(funcion.slice(0, inicio - 1) + funcion.slice(inicio));
      requestAnimationFrame(() => { entrada.focus(); entrada.setSelectionRange(inicio - 1, inicio - 1); });
    }
  };

  const teclas = [
    ["7", "8", "9", "/", "⌫"],
    ["4", "5", "6", "*", "("],
    ["1", "2", "3", "-", ")"],
    ["0", ".", "^", "+", "C"],
  ];
  const calcular = async (seleccion = null) => {
    setCargando(true); setError("");
    let entrada;
    let tipoElegido = tipo;
    if (seleccion) {
      entrada = seleccion.entrada;
      tipoElegido = seleccion.tipo;
      setTipo(seleccion.tipo);
    } else if (tipo === "derivada" || tipo === "integral" || tipo === "integral_definida") {
      entrada = { funcion };
      if (tipo === "integral_definida") Object.assign(entrada, { a: 0, b: 2 });
    } else if (tipo === "vector") {
      try { entrada = { operacion, u: JSON.parse(u), v: JSON.parse(v) }; }
      catch { setError("Los vectores deben escribirse como JSON, por ejemplo [2,3]."); setCargando(false); return; }
    } else if (tipo === "matriz") {
      entrada = { operacion, a: matriz, b: [[1, 0], [0, 1]] };
    } else {
      entrada = { funcion: "x^2+y^2", restriccion: "x+y-4" };
    }
    try {
      const data = await api("/api/laboratorio/calcular", { method: "POST", body: JSON.stringify({ tipo: tipoElegido, entrada }) });
      setResultado(data);
    } catch (e) { setError(e.message); }
    finally { setCargando(false); }
  };

  return (
    <main className="pagina laboratorio">
      <h1>Laboratorio matemático</h1>
      <section className="panel-controles">
        <label>Tipo de operación
          <select value={tipo} onChange={(e) => setTipo(e.target.value)}>
            <option value="derivada">Derivada</option><option value="integral">Integral indefinida</option>
            <option value="integral_definida">Integral definida</option><option value="vector">Vectores</option>
            <option value="matriz">Matrices</option><option value="lagrange">Lagrange</option>
          </select>
        </label>
        {(tipo === "derivada" || tipo.includes("integral") || tipo === "lagrange") &&
          <label className="entrada-calculadora">Entrada
            <input ref={entradaRef} value={funcion} onChange={(e) => setFuncion(e.target.value)} placeholder="Ejemplo: x^2" />
            <div className="teclado-cientifico">
              <div className="teclas-funciones">
                <button type="button" onClick={() => insertar("x")}>x</button>
                <button type="button" onClick={() => insertar("y")}>y</button>
                <button type="button" onClick={() => insertar("π")}>π</button>
                <button type="button" onClick={() => insertar("sin(")}>sin</button>
                <button type="button" onClick={() => insertar("cos(")}>cos</button>
                <button type="button" onClick={() => insertar("tan(")}>tan</button>
                <button type="button" onClick={() => insertar("ln(")}>ln</button>
                <button type="button" onClick={() => insertar("sqrt(")}>√</button>
              </div>
              <div className="teclado-numerico">
                {teclas.flat().map((tecla) => (
                  <button type="button" key={tecla} className={tecla === "C" ? "tecla-borrar" : ""} onClick={() => {
                    if (tecla === "⌫") borrar();
                    else if (tecla === "C") setFuncion("");
                    else insertar(tecla);
                  }}>{tecla}</button>
                ))}
              </div>
            </div>
          </label>}
        {tipo === "vector" && <>
          <label>Operación<select value={operacion} onChange={(e) => setOperacion(e.target.value)}><option value="suma">Suma</option><option value="punto">Producto punto</option><option value="norma">Norma</option><option value="cruz">Producto cruz</option><option value="proyeccion">Proyección</option></select></label>
          <label>Vector u<input value={u} onChange={(e) => setU(e.target.value)} /></label>
          <label>Vector v<input value={v} onChange={(e) => setV(e.target.value)} /></label>
        </>}
        {tipo === "matriz" && <>
          <label>Operación<select value={operacion} onChange={(e) => setOperacion(e.target.value)}><option value="determinante">Determinante</option><option value="inversa">Inversa</option><option value="producto">Producto</option><option value="gauss">Gauss-Jordan</option></select></label>
          <EditorMatriz valor={matriz} onChange={setMatriz} />
        </>}
        <button className="principal" onClick={() => calcular()} disabled={cargando}>{cargando ? "Calculando..." : "Calcular"}</button>
      </section>
      <div className="ejemplos">{ejemplos.map((e) => <button key={e.nombre} onClick={() => calcular(e)}>{e.nombre}</button>)}</div>
      {error && <div className="feedback error">{error}</div>}
      {resultado && <section className="salida">
        <div className="resultado-superior">
          <article className="resultado-final"><h2>Resultado</h2><Ecuacion latex={resultado.resultado} /></article>
          {resultado.grafica?.tipo !== "matriz" && <article className="grafica-panel"><h2>Gráfica</h2><Grafica datos={resultado.grafica} /></article>}
        </div>
        <h2>Pasos</h2>
        <div className="pasos-lista">{resultado.pasos.map((paso, i) => <PasoCard key={i} paso={paso} numero={i + 1} />)}</div>
      </section>}
    </main>
  );
}
