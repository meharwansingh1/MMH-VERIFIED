import { useId } from "react";

/**
 * A circular "passport stamp" badge — the signature visual motif of the
 * gateway page. Each vertical gets its own stamp text + glyph, echoing the
 * idea of a traveller's passport being stamped at each of the three gates.
 */
export default function Stamp({ label, glyph, tone = "light", className = "" }) {
  const pathId = useId();
  const ringColor = tone === "light" ? "#F5F5F5" : "#D4AF37";
  const textColor = tone === "light" ? "#F5F5F5" : "#D4AF37";

  return (
    <div className={`gate-stamp pointer-events-none select-none ${className}`}>
      <svg viewBox="0 0 140 140" className="h-24 w-24 md:h-28 md:w-28">
        <defs>
          <path
            id={pathId}
            d="M 70,70 m -52,0 a 52,52 0 1,1 104,0 a 52,52 0 1,1 -104,0"
          />
        </defs>
        <circle cx="70" cy="70" r="64" fill="none" stroke={ringColor} strokeWidth="1.5" opacity="0.9" />
        <circle cx="70" cy="70" r="52" fill="none" stroke={ringColor} strokeWidth="1" opacity="0.6" />
        <text fill={textColor} fontSize="10.5" letterSpacing="3" fontFamily="'DM Sans', sans-serif" fontWeight="600">
          <textPath href={`#${pathId}`} startOffset="0%">
            {label}
          </textPath>
        </text>
        <text
          x="70"
          y="78"
          textAnchor="middle"
          fill={textColor}
          fontSize="26"
          fontFamily="'Playfair Display', serif"
          fontStyle="italic"
        >
          {glyph}
        </text>
      </svg>
    </div>
  );
}
