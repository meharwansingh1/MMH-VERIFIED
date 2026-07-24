import { useEffect, useState } from "react";
import { IMAA } from "@/constants/testIds";
import { getAwardCategories, getAwardWinners } from "@/lib/api";

const FALLBACK_CATEGORIES = [
  { id: "c1", name: "Best Boutique Hotel", description: "Recognising exceptional independent hospitality." },
  { id: "c2", name: "Sustainable Tourism Initiative", description: "Honouring responsible, community-first travel." },
  { id: "c3", name: "Emerging Travel Brand", description: "Celebrating bold new voices in Indian travel." },
  { id: "c4", name: "Excellence in Travel Journalism", description: "For storytelling that moves the industry forward." },
];

export default function ImaaHome() {
  const [categories, setCategories] = useState(FALLBACK_CATEGORIES);
  const [winners, setWinners] = useState([]);

  useEffect(() => {
    getAwardCategories()
      .then((res) => {
        if (res.data?.length) setCategories(res.data);
      })
      .catch(() => {});
    getAwardWinners()
      .then((res) => setWinners(res.data || []))
      .catch(() => {});
  }, []);

  return (
    <div>
      <section data-testid={IMAA.hero} className="bg-black px-6 py-24 text-center text-white md:px-10 md:py-32">
        <p className="eyebrow text-gold">Vertical Two · Biennial Awards</p>
        <h1 className="mt-6 font-display text-5xl leading-tight md:text-7xl">IMAA</h1>
        <p className="mx-auto mt-6 max-w-xl font-body text-base leading-relaxed text-white/70 md:text-lg">
          Celebrating outstanding achievements in travel — the India Musafir Awards
          recognise excellence, innovation and the people shaping the future of
          global tourism, held every two years.
        </p>
      </section>

      <section className="mx-auto max-w-7xl px-6 py-16 md:px-10">
        <h2 className="mb-8 font-display text-3xl md:text-4xl">Award Categories</h2>
        <div data-testid={IMAA.categoriesGrid} className="grid grid-cols-1 gap-6 sm:grid-cols-2 lg:grid-cols-4">
          {categories.map((c) => (
            <div
              key={c.id}
              data-testid={IMAA.categoryCard}
              className="border border-black/10 p-6 transition-colors hover:border-gold"
            >
              <p className="font-display text-lg italic text-gold">Award</p>
              <h3 className="mt-2 font-display text-xl leading-snug">{c.name}</h3>
              <p className="mt-2 font-body text-sm leading-relaxed text-gray-600">{c.description}</p>
            </div>
          ))}
        </div>
      </section>

      {winners.length > 0 && (
        <section className="mx-auto max-w-7xl px-6 pb-16 md:px-10">
          <h2 className="mb-8 font-display text-3xl md:text-4xl">Past Winners</h2>
          <div data-testid={IMAA.winnersGrid} className="grid grid-cols-1 gap-6 sm:grid-cols-2 lg:grid-cols-3">
            {winners.map((w) => (
              <div key={w.id} data-testid={IMAA.winnerCard} className="border border-black/10 p-6">
                <p className="eyebrow text-gold">{w.category?.name}</p>
                <h3 className="mt-2 font-display text-lg">{w.recipient_name}</h3>
                <p className="mt-1 font-body text-sm text-gray-600">{w.year}</p>
              </div>
            ))}
          </div>
        </section>
      )}

      <section className="bg-mist px-6 py-16 text-center md:px-10 md:py-24">
        <p className="eyebrow text-gold">Nominations open every two years</p>
        <h2 className="mt-4 font-display text-3xl md:text-4xl">Nominate an Achiever</h2>
        <p className="mx-auto mt-4 max-w-md font-body text-sm text-gray-600">
          Know someone shaping the future of Indian travel? Put them forward for
          recognition.
        </p>
        <a
          href="/#contact"
          data-testid={IMAA.ctaNominate}
          className="mt-8 inline-block bg-black px-8 py-4 font-accent text-xs uppercase tracking-[0.2em] text-white transition-transform hover:-translate-y-1"
        >
          Submit a nomination
        </a>
      </section>
    </div>
  );
}
