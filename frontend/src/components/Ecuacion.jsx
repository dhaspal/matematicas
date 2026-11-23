import "katex/dist/katex.min.css";
import { BlockMath, InlineMath } from "react-katex";

export default function Ecuacion({ latex, inline = false }) {
  if (!latex) return null;
  return inline ? <InlineMath math={latex} /> : <BlockMath math={latex} />;
}
