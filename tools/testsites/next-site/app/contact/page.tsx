import { Page } from "@/components/Page";
import { pageMeta } from "@/lib/meta";

const TITLE = "Contact Acme Next support and sales teams";
export const metadata = pageMeta("/contact", TITLE, "Contact");

export default function P() {
  return <Page path="/contact" title={TITLE} label="Contact" />;
}
