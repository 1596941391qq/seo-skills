import { Page } from "@/components/Page";
import { pageMeta } from "@/lib/meta";

const TITLE = "Acme Next — test site home, what this site sells";
export const metadata = pageMeta("/", TITLE, "Home");

export default function Home() {
  return <Page path="/" title={TITLE} label="Home" />;
}
