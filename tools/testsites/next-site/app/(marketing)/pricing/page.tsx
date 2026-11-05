import { Page } from "@/components/Page";
import { pageMeta } from "@/lib/meta";

const TITLE = "Pricing for Acme Next plans and usage limits";
export const metadata = pageMeta("/pricing", TITLE, "Pricing");

export default function P() {
  return <Page path="/pricing" title={TITLE} label="Pricing" />;
}
