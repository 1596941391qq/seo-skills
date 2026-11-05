import type { MetadataRoute } from "next";
import { BASE } from "@/lib/plants";

const PATHS = ["/", "/about", "/pricing", "/blog", "/blog/a", "/blog/b", "/blog/c", "/docs", "/docs/start",
  "/docs/api", "/contact", "/team", "/old-page"];

export default function sitemap(): MetadataRoute.Sitemap {
  const now = new Date();
  return PATHS.map((p) => ({ url: BASE + p, lastModified: now }));
}
