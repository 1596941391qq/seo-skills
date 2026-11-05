import { Page } from "@/components/Page";
import { pageMeta } from "@/lib/meta";

const TITLE = "Acme Next blog: notes on shipping server pages";
export const metadata = pageMeta("/blog", TITLE, "Blog");

export default function P() {
  return <Page path="/blog" title={TITLE} label="Blog" />;
}
