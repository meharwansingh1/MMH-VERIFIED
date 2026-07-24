import { useEffect, useState } from "react";
import { PlayCircle } from "lucide-react";
import { PODCAST } from "@/constants/testIds";
import { getPodcastEpisodes } from "@/lib/api";

const FALLBACK_EPISODES = [
  { id: "e1", title: "Grab Your Backpack: Solo Travel Across India", duration_minutes: 38, guest_name: "Saakshi Rajat" },
  { id: "e2", title: "Building a Travel Brand from Scratch", duration_minutes: 44, guest_name: "Founder, True Joy Travels" },
  { id: "e3", title: "The Business of Sustainable Tourism", duration_minutes: 41, guest_name: "Industry Roundtable" },
];

export default function PodcastHome() {
  const [episodes, setEpisodes] = useState(FALLBACK_EPISODES);

  useEffect(() => {
    getPodcastEpisodes({ limit: 8 })
      .then((res) => {
        if (res.data?.length) setEpisodes(res.data);
      })
      .catch(() => {});
  }, []);

  return (
    <div>
      <section data-testid={PODCAST.hero} className="bg-black px-6 py-24 text-center text-white md:px-10 md:py-32">
        <p className="eyebrow text-gold">Vertical Three · On Air</p>
        <h1 className="mt-6 font-display text-5xl leading-tight md:text-7xl">The Musafir Podcast</h1>
        <p className="mx-auto mt-6 max-w-xl font-body text-base leading-relaxed text-white/70 md:text-lg">
          Engaging conversations with travellers, entrepreneurs and changemakers —
          inspiring stories, ideas and experiences from around the world.
        </p>
      </section>

      <section className="mx-auto max-w-4xl px-6 py-16 md:px-10">
        <h2 className="mb-8 font-display text-3xl md:text-4xl">Episodes</h2>
        <div data-testid={PODCAST.episodesList} className="divide-y divide-black/10 border-y border-black/10">
          {episodes.map((ep, i) => (
            <div
              key={ep.id}
              data-testid={PODCAST.episodeCard}
              className="flex items-center gap-6 py-6 transition-colors hover:bg-mist"
            >
              <span className="font-display text-2xl italic text-gold">
                {String(i + 1).padStart(2, "0")}
              </span>
              <PlayCircle size={28} className="shrink-0 text-black/70" />
              <div className="flex-1">
                <h3 className="font-display text-lg leading-snug">{ep.title}</h3>
                <p className="mt-1 font-body text-sm text-gray-600">
                  {ep.guest_name ? `with ${ep.guest_name}` : "Musafir Podcast"}
                  {ep.duration_minutes ? ` · ${ep.duration_minutes} min` : ""}
                </p>
              </div>
            </div>
          ))}
        </div>
      </section>

      <section className="bg-mist px-6 py-16 text-center md:px-10 md:py-24">
        <p className="eyebrow text-gold">Have a story worth telling?</p>
        <h2 className="mt-4 font-display text-3xl md:text-4xl">Be a Guest</h2>
        <p className="mx-auto mt-4 max-w-md font-body text-sm text-gray-600">
          We're always looking for travellers, founders and changemakers to feature.
        </p>
        <a
          href="/#contact"
          data-testid={PODCAST.ctaGuest}
          className="mt-8 inline-block bg-black px-8 py-4 font-accent text-xs uppercase tracking-[0.2em] text-white transition-transform hover:-translate-y-1"
        >
          Pitch yourself
        </a>
      </section>
    </div>
  );
}
