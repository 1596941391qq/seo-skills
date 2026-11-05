import { Page } from "@/components/Page";
import { pageMeta } from "@/lib/meta";

const TITLE = "The Acme Next team and how to reach each of us";
export const metadata = pageMeta("/team", TITLE, "Team");

export default function P() {
  return <Page path="/team" title={TITLE} label="Team" />;
}
