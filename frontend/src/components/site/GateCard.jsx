import { Link } from "react-router-dom";
import { ArrowUpRight } from "lucide-react";
import Stamp from "./Stamp";

export default function GateCard({
  to,
  image,
  eyebrow,
  title,
  description,
  stampLabel,
  stampGlyph,
  testId,
}) {
  return (
    <Link
      to={to}
      data-testid={testId}
      className="gate-card group relative flex aspect-[3/4] flex-col justify-end overflow-hidden bg-charcoal focus:outline-none focus-visible:ring-2 focus-visible:ring-gold focus-visible:ring-offset-2"
    >
      <img
        src={image}
        alt=""
        className="gate-image absolute inset-0 h-full w-full object-cover"
        loading="lazy"
      />
      <div className="absolute inset-0 bg-gradient-to-t from-black via-black/30 to-black/10" />

      <Stamp
        label={stampLabel}
        glyph={stampGlyph}
        className="absolute right-6 top-6"
      />

      <div className="relative z-10 p-8 md:p-10">
        <p className="eyebrow text-gold">{eyebrow}</p>
        <h3 className="mt-3 font-display text-3xl leading-tight text-white md:text-4xl">
          {title}
        </h3>
        <p className="mt-4 max-w-xs font-body text-sm leading-relaxed text-white/70">
          {description}
        </p>
        <div className="mt-6 flex items-center gap-2 font-accent text-xs uppercase tracking-[0.2em] text-white">
          Start exploring
          <ArrowUpRight size={16} className="gate-arrow" />
        </div>
      </div>
    </Link>
  );
}
