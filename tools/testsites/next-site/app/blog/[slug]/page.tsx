import { notFound } from "next/navigation";
import { Page } from "@/components/Page";
import { pageMeta } from "@/lib/meta";
import posts from "@/content/posts.json";

type Params = { slug: string };
const POSTS = posts as Record<string, { title: string }>;

export function generateStaticParams() {
  return Object.keys(POSTS).map((slug) => ({ slug }));
}

export async function generateMetadata({ params }: { params: Promise<Params> }) {
  const { slug } = await params;
  const post = POSTS[slug];
  return post ? pageMeta(`/blog/${slug}`, post.title, `Post ${slug}`) : {};
}

export default async function Post({ params }: { params: Promise<Params> }) {
  const { slug } = await params;
  const post = POSTS[slug];
  if (!post) notFound();
  return <Page path={`/blog/${slug}`} title={post.title} label={`Post ${slug}`} />;
}
