import { readFileSync } from "node:fs";
import { join } from "node:path";

// 构建时读预埋清单:{"/about": "title_missing", ...}
export function plantFor(path: string): string | undefined {
  try {
    const p = JSON.parse(readFileSync(join(process.cwd(), "plants.json"), "utf8"));
    return p[path];
  } catch {
    return undefined;
  }
}

export const BASE = process.env.SITE_BASE || "http://127.0.0.1:8602";
