import { Page } from "@/components/Page";
import { pageMeta } from "@/lib/meta";

const TITLE = "Old page that moved to the new docs location";
export const metadata = pageMeta("/old-page", TITLE, "Old page");

export default function P() {
  return <Page path="/old-page" title={TITLE} label="Old page" />;
}
