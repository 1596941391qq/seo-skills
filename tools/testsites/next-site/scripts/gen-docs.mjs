// 文档页数据的真源:改这里,再跑 `npm run gen` 生成 lib/docs.generated.ts
import { writeFileSync } from "node:fs";

const DOCS = {
  start: { title: "Getting started with Acme Next in five minutes" },
  api: { title: "Acme Next API reference for build hooks" },
};

const header = "/* 自动生成：node scripts/gen-docs.mjs —— 手改会被覆盖,改 scripts/gen-docs.mjs */\n";
writeFileSync(
  new URL("../lib/docs.generated.ts", import.meta.url),
  header + "export const DOCS: Record<string, { title: string }> = " + JSON.stringify(DOCS, null, 2) + ";\n",
);
