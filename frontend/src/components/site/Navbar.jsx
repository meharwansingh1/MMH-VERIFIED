import { useEffect, useState } from "react";
import { Link, NavLink } from "react-router-dom";
import { Menu, X } from "lucide-react";
import { GATEWAY } from "@/constants/testIds";

const LINKS = [
  { to: "/", label: "Home", testId: GATEWAY.navLinkHome },
  { to: "/musafir-media-hub", label: "Musafir Media Hub", testId: GATEWAY.navLinkHub },
  { to: "/imaa", label: "IMAA", testId: GATEWAY.navLinkImaa },
  { to: "/the-musafir-podcast", label: "The Musafir Podcast", testId: GATEWAY.navLinkPodcast },
];

export default function Navbar() {
  const [scrolled, setScrolled] = useState(false);
  const [open, setOpen] = useState(false);

  useEffect(() => {
    const onScroll = () => setScrolled(window.scrollY > 12);
    window.addEventListener("scroll", onScroll);
    return () => window.removeEventListener("scroll", onScroll);
  }, []);

  return (
    <header
      data-testid={GATEWAY.nav}
      className={`sticky top-0 z-50 border-b transition-colors duration-300 ${
        scrolled
          ? "border-black/10 bg-white/75 backdrop-blur-xl"
          : "border-transparent bg-transparent"
      }`}
    >
      <div className="mx-auto flex max-w-7xl items-center justify-between px-6 py-5 md:px-10">
        <Link
          to="/"
          data-testid={GATEWAY.navLogo}
          className="font-display text-lg tracking-tight text-black"
        >
          Musafir <span className="text-gold">Media</span> Publications
        </Link>

        <nav className="hidden items-center gap-8 lg:flex">
          {LINKS.map((l) => (
            <NavLink
              key={l.to}
              to={l.to}
              data-testid={l.testId}
              className={({ isActive }) =>
                `font-accent text-xs uppercase tracking-[0.18em] transition-colors hover:text-gold ${
                  isActive ? "text-black" : "text-black/60"
                }`
              }
            >
              {l.label}
            </NavLink>
          ))}
          <a
            href="#contact"
            data-testid={GATEWAY.navLinkContact}
            className="border border-black px-5 py-2.5 font-accent text-xs uppercase tracking-[0.18em] text-black transition-colors hover:bg-black hover:text-white"
          >
            Contact
          </a>
        </nav>

        <button
          aria-label={open ? "Close menu" : "Open menu"}
          className="text-black lg:hidden"
          onClick={() => setOpen((v) => !v)}
        >
          {open ? <X size={24} /> : <Menu size={24} />}
        </button>
      </div>

      {open && (
        <nav className="flex flex-col gap-1 border-t border-black/10 bg-white px-6 pb-6 pt-2 lg:hidden">
          {LINKS.map((l) => (
            <NavLink
              key={l.to}
              to={l.to}
              onClick={() => setOpen(false)}
              className="border-b border-black/5 py-3 font-accent text-sm uppercase tracking-[0.15em] text-black/80"
            >
              {l.label}
            </NavLink>
          ))}
          <a
            href="#contact"
            onClick={() => setOpen(false)}
            className="py-3 font-accent text-sm uppercase tracking-[0.15em] text-gold"
          >
            Contact
          </a>
        </nav>
      )}
    </header>
  );
}
