import type { Metadata } from "next";
import { BASE, plantFor } from "./plants";

export function pageMeta(path: string, title: string, label: string): Metadata {
  const plant = plantFor(path);
  const m: Metadata = {
    alternates: { canonical: BASE + path },
    openGraph: { title, description: `${label} page of Acme Next`, images: [BASE + "/og.png"] },
  };
  if (plant === "title_missing") m.title = null;
  else if (plant === "title_too_long") m.title = `${title} — and a much longer tail that keeps going well past any sensible limit`;
  else m.title = title;
  if (plant !== "desc_missing") m.description = `${title}. Read the details, see examples and find the next step on this page.`;
  if (plant === "noindex") m.robots = { index: false };
  if (plant === "og_missing") m.openGraph = { title, description: `${label} page of Acme Next` };
  return m;
}
