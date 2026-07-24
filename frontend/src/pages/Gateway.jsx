import { useState } from "react";
import { GATEWAY } from "@/constants/testIds";
import GateCard from "@/components/site/GateCard";
import { submitEnquiry } from "@/lib/api";

const BRANDS = [
  "OA DMC", "ITB India", "IATO", "FHTR", "Madhya Pradesh Tourism",
  "EaseMyTrip", "India Tourism", "Devdiscourse", "Business Traveller India",
  "Bureaucracy India Magazine",
];

export default function Gateway() {
  return (
    <div className="bg-white">
      {/* ---------------- Hero ---------------- */}
      <section
        data-testid={GATEWAY.hero}
        className="relative flex min-h-[80vh] flex-col items-center justify-center overflow-hidden bg-black px-6 py-28 text-center text-white md:px-10"
      >
        <p className="eyebrow text-gold">Musafir Media Publications Pvt Ltd</p>
        <h1
          data-testid={GATEWAY.heroHeadline}
          className="mt-6 max-w-4xl font-display text-5xl leading-[1.05] tracking-tight md:text-7xl"
        >
          Three Paths.
          <br />
          One Bold Journey.
        </h1>
        <div className="mt-8 h-px w-24 bg-gold" />
        <p className="mt-8 max-w-xl font-body text-base leading-relaxed text-white/70 md:text-lg">
          We are driven by the spirit of exploration — just like a Musafir, a traveller
          who never stops discovering the world. Choose a gate below to begin.
        </p>
      </section>

      {/* ---------------- The three gates ---------------- */}
      <section className="mx-auto max-w-7xl px-6 py-16 md:px-10 md:py-24">
        <div className="grid grid-cols-1 gap-6 md:grid-cols-3">
          <GateCard
            to="/musafir-media-hub"
            testId={GATEWAY.gateHub}
            image="https://images.unsplash.com/photo-1724405095085-06d4246a2af8?crop=entropy&cs=srgb&fm=jpg&ixid=M3w4NjA2MjJ8MHwxfHNlYXJjaHwyfHxtYWdhemluZSUyMGVkaXRvcmlhbCUyMG1vZGVsfGVufDB8fHx8MTc4NDEyODIyMXww&ixlib=rb-4.1.0&q=85"
            eyebrow="Vertical One · Est. 2018"
            title="Musafir Media Hub"
            stampLabel="MUSAFIR · MEDIA HUB ·"
            stampGlyph="MMH"
            description="A creative platform of newsletters and bilingual print & digital magazines — fresh stories across travel, lifestyle and culture."
          />
          <GateCard
            to="/imaa"
            testId={GATEWAY.gateImaa}
            image="https://images.unsplash.com/photo-1650240852447-46505dba4726?crop=entropy&cs=srgb&fm=jpg&ixid=M3w4NjAzMzJ8MHwxfHNlYXJjaHwyfHxnb2xkJTIwdHJvcGh5JTIwYXdhcmQlMjBjZXJlbW9ueXxlbnwwfHx8fDE3ODQxMjgyMjF8MA&ixlib=rb-4.1.0&q=85"
            eyebrow="Vertical Two · Biennial"
            title="IMAA"
            stampLabel="INDIA MUSAFIR AWARDS ·"
            stampGlyph="IMAA"
            description="Celebrating outstanding achievements in travel — recognising excellence, innovation and the people shaping the future of global tourism."
          />
          <GateCard
            to="/the-musafir-podcast"
            testId={GATEWAY.gatePodcast}
            image="https://images.pexels.com/photos/31213674/pexels-photo-31213674.jpeg?auto=compress&cs=tinysrgb&dpr=2&h=650&w=940"
            eyebrow="Vertical Three · On Air"
            title="The Musafir Podcast"
            stampLabel="THE MUSAFIR PODCAST ·"
            stampGlyph="TMP"
            description="Engaging conversations with travellers, entrepreneurs and changemakers — inspiring stories and ideas from around the world."
          />
        </div>
      </section>

      {/* ---------------- About ---------------- */}
      <section data-testid={GATEWAY.about} className="mx-auto max-w-7xl px-6 py-16 md:px-10 md:py-24">
        <div className="grid grid-cols-1 gap-12 lg:grid-cols-12">
          <div className="lg:col-span-4">
            <p className="eyebrow text-gold">About</p>
            <h2 className="mt-4 font-display text-3xl leading-tight md:text-4xl">
              A decade of trusted travel storytelling.
            </h2>
          </div>
          <div className="space-y-5 font-body text-base leading-relaxed text-gray-700 lg:col-span-8">
            <p>
              Launched in November 2018, Musafir Media Hub is a B2B travel media platform,
              now available in both print and digital formats, aiming to showcase India to
              the world as a role model for respect, sustainability and exploration.
            </p>
            <p>
              With over a decade of experience in the travel industry, we've built a
              reputation for trustworthy, informative and inspiring content that stands out
              in a competitive market — delivered through daily newsletters, social media,
              a bilingual print and digital magazine, and The Musafir Podcast.
            </p>
            <p>
              Alongside our editorial work, we take pride in recognising excellence in the
              travel trade through the IMAA Awards, held every two years to celebrate
              outstanding contributions by individuals and organisations shaping the future
              of travel.
            </p>
          </div>
        </div>
      </section>

      {/* ---------------- Brands marquee ---------------- */}
      <section className="border-y border-black/10 bg-mist py-14">
        <p className="eyebrow mb-8 text-center text-ash">Brands we've worked with</p>
        <div data-testid={GATEWAY.brandsMarquee} className="marquee-viewport overflow-hidden">
          <div className="marquee-track gap-16 pr-16">
            {[...BRANDS, ...BRANDS].map((b, i) => (
              <span
                key={`${b}-${i}`}
                className="font-display text-xl italic text-black/40 whitespace-nowrap"
              >
                {b}
              </span>
            ))}
          </div>
        </div>
      </section>

      {/* ---------------- Contact ---------------- */}
      <ContactSection />
    </div>
  );
}

function ContactSection() {
  const [form, setForm] = useState({ first_name: "", last_name: "", email: "", message: "" });
  const [status, setStatus] = useState("idle");

  const onChange = (e) => setForm({ ...form, [e.target.name]: e.target.value });

  const onSubmit = async (e) => {
    e.preventDefault();
    setStatus("loading");
    try {
      await submitEnquiry({ ...form, kind: "contact", source_page: "gateway" });
      setStatus("done");
      setForm({ first_name: "", last_name: "", email: "", message: "" });
    } catch {
      setStatus("error");
    }
  };

  return (
    <section id="contact" className="mx-auto max-w-7xl px-6 py-16 md:px-10 md:py-24">
      <div className="grid grid-cols-1 gap-12 lg:grid-cols-2">
        <div>
          <p className="eyebrow text-gold">Contact us</p>
          <h2 className="mt-4 font-display text-3xl leading-tight md:text-4xl">
            Let's start a conversation.
          </h2>
          <p className="mt-4 max-w-md font-body text-sm leading-relaxed text-gray-600">
            Media partnerships, advertising, award nominations or podcast guest
            pitches — tell us what you have in mind.
          </p>
        </div>
        <form onSubmit={onSubmit} data-testid={GATEWAY.contactForm} className="space-y-4">
          <div className="grid grid-cols-1 gap-4 sm:grid-cols-2">
            <input
              name="first_name"
              required
              value={form.first_name}
              onChange={onChange}
              placeholder="First name*"
              data-testid={GATEWAY.contactFirstName}
              className="border border-black/15 px-4 py-3 font-body text-sm focus:border-gold focus:outline-none"
            />
            <input
              name="last_name"
              value={form.last_name}
              onChange={onChange}
              placeholder="Last name"
              data-testid={GATEWAY.contactLastName}
              className="border border-black/15 px-4 py-3 font-body text-sm focus:border-gold focus:outline-none"
            />
          </div>
          <input
            name="email"
            type="email"
            required
            value={form.email}
            onChange={onChange}
            placeholder="Email*"
            data-testid={GATEWAY.contactEmail}
            className="w-full border border-black/15 px-4 py-3 font-body text-sm focus:border-gold focus:outline-none"
          />
          <textarea
            name="message"
            rows={4}
            value={form.message}
            onChange={onChange}
            placeholder="Write a message"
            data-testid={GATEWAY.contactMessage}
            className="w-full border border-black/15 px-4 py-3 font-body text-sm focus:border-gold focus:outline-none"
          />
          <button
            type="submit"
            data-testid={GATEWAY.contactSubmit}
            className="bg-black px-8 py-4 font-accent text-xs uppercase tracking-[0.2em] text-white transition-transform hover:-translate-y-1"
          >
            {status === "loading" ? "Sending..." : "Submit"}
          </button>
          {status === "done" && (
            <p className="font-body text-xs text-emerald-700">
              Thanks — we'll be in touch shortly.
            </p>
          )}
          {status === "error" && (
            <p className="font-body text-xs text-gray-500">
              Couldn't reach the server just now — please try again shortly.
            </p>
          )}
        </form>
      </div>
    </section>
  );
}
