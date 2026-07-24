import { useEffect, useState } from "react";
import { HUB } from "@/constants/testIds";
import { getArticles, getMagazineCurrentIssue } from "@/lib/api";

const FALLBACK_ARTICLES = [
  {
    id: "f1",
    title: "Inside India's Quiet Luxury Travel Renaissance",
    excerpt: "How boutique stays and slow-travel itineraries are redefining Indian hospitality.",
    category: { name: "Lifestyle" },
    image: "https://images.unsplash.com/photo-1782835576404-f5eaddd63ac3?crop=entropy&cs=srgb&fm=jpg&q=85",
  },
  {
    id: "f2",
    title: "The New Architecture of Hospitality",
    excerpt: "Minimal, sustainable design is becoming the signature of India's newest hotels.",
    category: { name: "Architecture" },
    image: "https://images.unsplash.com/photo-1483366774565-c783b9f70e2c?crop=entropy&cs=srgb&fm=jpg&q=85",
  },
  {
    id: "f3",
    title: "Editorial Notes: On the Road with Musafir",
    excerpt: "Field dispatches from our editorial team travelling across the subcontinent.",
    category: { name: "Editorial" },
    image: "https://images.pexels.com/photos/15713593/pexels-photo-15713593.jpeg?auto=compress&cs=tinysrgb&h=650&w=940",
  },
];

export default function HubHome() {
  const [articles, setArticles] = useState(FALLBACK_ARTICLES);
  const [issue, setIssue] = useState(null);

  useEffect(() => {
    getArticles({ limit: 6 })
      .then((res) => {
        if (res.data?.items?.length) setArticles(res.data.items);
      })
      .catch(() => {});
    getMagazineCurrentIssue()
      .then((res) => setIssue(res.data))
      .catch(() => {});
  }, []);

  return (
    <div>
      <section data-testid={HUB.hero} className="bg-black px-6 py-24 text-center text-white md:px-10 md:py-32">
        <p className="eyebrow text-gold">Vertical One · Est. November 2018</p>
        <h1 className="mt-6 font-display text-5xl leading-tight md:text-7xl">Musafir Media Hub</h1>
        <p className="mx-auto mt-6 max-w-xl font-body text-base leading-relaxed text-white/70 md:text-lg">
          A B2B travel media platform bringing India's tourism and hospitality story to
          the world — through newsletters, our bilingual print & digital magazine, and
          daily editorial coverage.
        </p>
      </section>

      {issue && (
        <section data-testid={HUB.issueCallout} className="mx-auto max-w-7xl px-6 py-16 md:px-10">
          <div className="grid grid-cols-1 items-center gap-8 border border-black/10 p-8 md:grid-cols-3 md:p-12">
            {issue.cover_image && (
              <img src={issue.cover_image} alt={issue.title} className="aspect-[3/4] w-full object-cover md:col-span-1" />
            )}
            <div className="md:col-span-2">
              <p className="eyebrow text-gold">Current issue</p>
              <h3 className="mt-3 font-display text-2xl md:text-3xl">{issue.title}</h3>
              <p className="mt-3 font-body text-sm leading-relaxed text-gray-600">{issue.description}</p>
            </div>
          </div>
        </section>
      )}

      <section className="mx-auto max-w-7xl px-6 pb-16 md:px-10">
        <div className="mb-8 flex items-end justify-between">
          <h2 className="font-display text-3xl md:text-4xl">Latest Stories</h2>
        </div>
        <div data-testid={HUB.articlesGrid} className="grid grid-cols-1 gap-8 sm:grid-cols-2 lg:grid-cols-3">
          {articles.map((a) => (
            <article key={a.id} data-testid={HUB.articleCard} className="group cursor-pointer">
              <div className="aspect-[4/5] overflow-hidden">
                <img
                  src={a.cover_image || a.image}
                  alt={a.title}
                  className="h-full w-full object-cover transition-transform duration-700 ease-out group-hover:scale-105"
                />
              </div>
              <p className="eyebrow mt-4 text-gold">{a.category?.name || "Musafir Media Hub"}</p>
              <h3 className="mt-2 font-display text-xl leading-snug">{a.title}</h3>
              <p className="mt-2 font-body text-sm leading-relaxed text-gray-600">{a.excerpt}</p>
            </article>
          ))}
        </div>
      </section>

      <section className="bg-mist px-6 py-16 text-center md:px-10 md:py-24">
        <p className="eyebrow text-gold">Work with us</p>
        <h2 className="mt-4 font-display text-3xl md:text-4xl">Advertise in the Hub</h2>
        <p className="mx-auto mt-4 max-w-md font-body text-sm text-gray-600">
          Reach a trusted, engaged travel-trade audience across print and digital.
        </p>
        <a
          href="/#contact"
          data-testid={HUB.ctaAdvertise}
          className="mt-8 inline-block bg-black px-8 py-4 font-accent text-xs uppercase tracking-[0.2em] text-white transition-transform hover:-translate-y-1"
        >
          Get the media kit
        </a>
      </section>
    </div>
  );
}
