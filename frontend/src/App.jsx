import { Routes, Route, Link } from "react-router-dom";
import Inicio from "./pages/Inicio";
import DueloCartas from "./pages/DueloCartas";
import PasoAPaso from "./pages/PasoAPaso";
import Laboratorio from "./pages/Laboratorio";
import JefeFinal from "./pages/JefeFinal";
import CasosForenses from "./pages/CasosForenses";
import BarraProgreso from "./components/BarraProgreso";
import { useProgreso } from "./hooks/useProgreso";

export default function App() {
  const progresoState = useProgreso();
  const { progreso, sumarAcierto, sumarError, reiniciar } = progresoState;
  return (
    <>
      <BarraProgreso progreso={progreso} reiniciar={reiniciar} />
      <nav className="nav"><Link to="/">Inicio</Link><Link to="/laboratorio">Laboratorio</Link><Link to="/paso">Paso a paso</Link><Link to="/duelo">Duelo</Link><Link to="/jefe">Jefe</Link></nav>
      <Routes>
        <Route path="/" element={<Inicio />} />
        <Route path="/duelo" element={<DueloCartas sumarAcierto={sumarAcierto} sumarError={sumarError} />} />
        <Route path="/paso" element={<PasoAPaso sumarAcierto={sumarAcierto} sumarError={sumarError} />} />
        <Route path="/laboratorio" element={<Laboratorio />} />
        <Route path="/jefe" element={<JefeFinal sumarAcierto={sumarAcierto} sumarError={sumarError} />} />
        <Route path="/casos" element={<CasosForenses />} />
      </Routes>
    </>
  );
}
