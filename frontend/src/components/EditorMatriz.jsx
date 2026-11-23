export default function EditorMatriz({ valor, onChange, filas = 2, columnas = 2 }) {
  const matriz = Array.isArray(valor) ? valor : Array.from({ length: filas }, () => Array(columnas).fill(0));
  const cambiar = (fila, columna, texto) => {
    const copia = matriz.map((r) => [...r]);
    copia[fila][columna] = Number(texto);
    onChange(copia);
  };
  return (
    <div className="editor-matriz">
      {matriz.map((fila, i) => (
        <div key={i} className="fila-matriz">
          {fila.map((valorCelda, j) => <input key={j} type="number" value={valorCelda} onChange={(e) => cambiar(i, j, e.target.value)} />)}
        </div>
      ))}
    </div>
  );
}
