import { Page } from "@/components/Page";
import { pageMeta } from "@/lib/meta";

const TITLE = "Acme Next docs: install, configure and deploy";
export const metadata = pageMeta("/docs", TITLE, "Docs");

export default function P() {
  return <Page path="/docs" title={TITLE} label="Docs" />;
}
