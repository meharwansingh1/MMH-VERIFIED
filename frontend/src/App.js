import "@/App.css";
import { BrowserRouter, Routes, Route } from "react-router-dom";
import { Toaster } from "@/components/ui/sonner";
import Layout from "@/components/site/Layout";
import Gateway from "@/pages/Gateway";
import HubHome from "@/pages/hub/HubHome";
import ImaaHome from "@/pages/imaa/ImaaHome";
import PodcastHome from "@/pages/podcast/PodcastHome";

function NotFound() {
  return (
    <div className="flex min-h-[60vh] flex-col items-center justify-center px-6 text-center">
      <p className="eyebrow text-gold">404</p>
      <h1 className="mt-4 font-display text-4xl">This path doesn't exist yet.</h1>
      <a href="/" className="mt-8 font-accent text-xs uppercase tracking-[0.2em] underline">
        Back to the gateway
      </a>
    </div>
  );
}

function App() {
  return (
    <BrowserRouter>
      <Toaster position="top-right" />
      <Routes>
        <Route element={<Layout />}>
          <Route index element={<Gateway />} />
          <Route path="musafir-media-hub" element={<HubHome />} />
          <Route path="imaa" element={<ImaaHome />} />
          <Route path="the-musafir-podcast" element={<PodcastHome />} />
          <Route path="*" element={<NotFound />} />
        </Route>
      </Routes>
    </BrowserRouter>
  );
}

export default App;
