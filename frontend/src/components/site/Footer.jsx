import { useState } from "react";
import { Link } from "react-router-dom";
import { Instagram, Facebook, Twitter, Mail, Phone, MapPin } from "lucide-react";
import { GATEWAY } from "@/constants/testIds";
import { subscribeToNewsletter } from "@/lib/api";

export default function Footer() {
  const [email, setEmail] = useState("");
  const [status, setStatus] = useState("idle"); // idle | loading | done | error

  const onSubmit = async (e) => {
    e.preventDefault();
    if (!email) return;
    setStatus("loading");
    try {
      await subscribeToNewsletter({ email, source: "footer" });
      setStatus("done");
      setEmail("");
    } catch {
      setStatus("error");
    }
  };

  return (
    <footer data-testid={GATEWAY.footer} className="border-t border-white/10 bg-black text-white">
      <div className="mx-auto grid max-w-7xl grid-cols-1 gap-12 px-6 py-16 md:grid-cols-4 md:px-10">
        <div className="md:col-span-2">
          <p className="font-display text-2xl">
            Musafir <span className="text-gold">Media</span> Publications
          </p>
          <p className="mt-4 max-w-sm font-body text-sm leading-relaxed text-white/60">
            Driven by the spirit of exploration — just like a Musafir, a traveller who
            never stops discovering. Three verticals, one bold journey across India's
            travel, tourism and hospitality landscape.
          </p>
          <form
            onSubmit={onSubmit}
            data-testid={GATEWAY.newsletterForm}
            className="mt-8 flex max-w-sm border border-white/20"
          >
            <input
              type="email"
              required
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              placeholder="Your email"
              data-testid={GATEWAY.newsletterEmail}
              className="w-full bg-transparent px-4 py-3 font-body text-sm text-white placeholder:text-white/40 focus:outline-none"
            />
            <button
              type="submit"
              data-testid={GATEWAY.newsletterSubmit}
              className="whitespace-nowrap bg-gold px-5 py-3 font-accent text-xs uppercase tracking-[0.15em] text-black transition-transform hover:-translate-y-0.5"
            >
              {status === "loading" ? "..." : "Subscribe"}
            </button>
          </form>
          {status === "done" && (
            <p className="mt-2 font-body text-xs text-gold">You're subscribed. Welcome aboard.</p>
          )}
          {status === "error" && (
            <p className="mt-2 font-body text-xs text-white/50">
              Couldn't reach the server just now — try again shortly.
            </p>
          )}
        </div>

        <div>
          <p className="eyebrow text-gold">Verticals</p>
          <ul className="mt-4 space-y-2 font-body text-sm text-white/70">
            <li><Link to="/musafir-media-hub" className="hover:text-white">Musafir Media Hub</Link></li>
            <li><Link to="/imaa" className="hover:text-white">IMAA</Link></li>
            <li><Link to="/the-musafir-podcast" className="hover:text-white">The Musafir Podcast</Link></li>
          </ul>
        </div>

        <div>
          <p className="eyebrow text-gold">Reach us</p>
          <ul className="mt-4 space-y-3 font-body text-sm text-white/70">
            <li className="flex items-start gap-2">
              <MapPin size={16} className="mt-0.5 shrink-0 text-white/40" />
              61 Basement, Defence Enclave, Preet Vihar, New Delhi – 110092
            </li>
            <li className="flex items-center gap-2">
              <Phone size={16} className="shrink-0 text-white/40" />
              <a href="tel:+919650805752" className="hover:text-white">+91 96508 05752</a>
            </li>
            <li className="flex items-center gap-2">
              <Mail size={16} className="shrink-0 text-white/40" />
              <a href="mailto:dimple@musafirmediahub.com" className="hover:text-white">
                dimple@musafirmediahub.com
              </a>
            </li>
          </ul>
          <div className="mt-5 flex gap-4">
            <a href="#" aria-label="Instagram" className="text-white/50 hover:text-gold"><Instagram size={18} /></a>
            <a href="#" aria-label="Facebook" className="text-white/50 hover:text-gold"><Facebook size={18} /></a>
            <a href="#" aria-label="Twitter" className="text-white/50 hover:text-gold"><Twitter size={18} /></a>
          </div>
        </div>
      </div>
      <div className="border-t border-white/10 px-6 py-6 text-center font-body text-xs text-white/40 md:px-10">
        © {new Date().getFullYear()} Musafir Media Publications Pvt Ltd. All rights reserved.
      </div>
    </footer>
  );
}
