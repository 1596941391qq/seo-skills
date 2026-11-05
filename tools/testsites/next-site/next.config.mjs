import { readFileSync } from "node:fs";

// 预埋状态由 run_example3 写进 plants.json(不进 git);没有就是干净站
function plants() {
  try { return JSON.parse(readFileSync(new URL("./plants.json", import.meta.url), "utf8")); } catch { return {}; }
}

export default {
  trailingSlash: false,
  async redirects() {
    const p = plants();
    return p["/old-page"] === "redirect_301"
      ? [{ source: "/old-page", destination: "/docs", statusCode: 301 }]
      : [];
  },
};
