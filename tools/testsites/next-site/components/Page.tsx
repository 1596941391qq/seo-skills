import { notFound } from "next/navigation";
import { BASE, plantFor } from "@/lib/plants";

const FILLER =
  "Acme Next builds server-rendered pages that load fast and stay easy to audit. Every page here answers one question " +
  "in its first paragraph, then gives the details a reader needs to act. We keep the markup semantic, the images " +
  "described, and the links few and relevant. The team writes each page by hand, checks it against a short list, " +
  "and ships it only when the list is green. This paragraph exists so the page has enough real text for a search " +
  "engine to understand the topic without guessing. It talks about builds, caching, release checks, documentation, " +
  "pricing, support and the people who run the project. Readers who want more can follow the links in the " +
  "navigation, read the docs, or contact the team directly through the contact page listed in the footer.";

export function Page({ path, title, label }: { path: string; title: string; label: string }) {
  const plant = plantFor(path);
  if (plant === "status_404") notFound();
  const jsonld = { "@context": "https://schema.org", "@type": "WebPage", name: title, url: BASE + path };
  return (
    <main>
      <article>
        {plant !== "jsonld_missing" && (
          <script type="application/ld+json" dangerouslySetInnerHTML={{ __html: JSON.stringify(jsonld) }} />
        )}
        <h1>{title}</h1>
        {plant === "h1_multiple" && <h1>Second heading one</h1>}
        <p>{label} answers it directly: {FILLER}</p>
        <h2>Details</h2>
        <p>{FILLER}</p>
        {plant === "heading_skip" ? <h4>Skipped level</h4> : <h3>Background</h3>}
        <p>{FILLER}</p>
        <h2>Next steps</h2>
        <section>
          <p>{FILLER}</p>
          {[0, 1, 2].map((i) =>
            plant === "img_alt_missing" ? (
              // eslint-disable-next-line @next/next/no-img-element, jsx-a11y/alt-text
              <img key={i} src={`/img${i}.png`} width={10} height={10} />
            ) : (
              // eslint-disable-next-line @next/next/no-img-element
              <img key={i} src={`/img${i}.png`} alt={`Diagram of the ${label} page`} width={10} height={10} />
            ),
          )}
        </section>
      </article>
    </main>
  );
}
