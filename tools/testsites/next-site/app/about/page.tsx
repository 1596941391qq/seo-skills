import { Page } from "@/components/Page";
import { pageMeta } from "@/lib/meta";

const TITLE = "About Acme Next: who we are and what we build";
export const metadata = pageMeta("/about", TITLE, "About");

export default function P() {
  return <Page path="/about" title={TITLE} label="About" />;
}
