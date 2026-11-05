import { notFound } from "next/navigation";
import { Page } from "@/components/Page";
import { pageMeta } from "@/lib/meta";
import { DOCS } from "@/lib/docs.generated";

type Params = { path: string[] };

export function generateStaticParams() {
  return Object.keys(DOCS).map((k) => ({ path: [k] }));
}

export async function generateMetadata({ params }: { params: Promise<Params> }) {
  const { path } = await params;
  const doc = DOCS[path.join("/")];
  return doc ? pageMeta(`/docs/${path.join("/")}`, doc.title, `Doc ${path.join("/")}`) : {};
}

export default async function Doc({ params }: { params: Promise<Params> }) {
  const { path } = await params;
  const key = path.join("/");
  const doc = DOCS[key];
  if (!doc) notFound();
  return <Page path={`/docs/${key}`} title={doc.title} label={`Doc ${key}`} />;
}
