import type { MetadataRoute } from "next";
import { BASE } from "@/lib/plants";

export default function robots(): MetadataRoute.Robots {
  return { rules: [{ userAgent: "*", allow: "/" }], sitemap: BASE + "/sitemap.xml" };
}
