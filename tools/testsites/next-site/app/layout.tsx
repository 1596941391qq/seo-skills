import Link from "next/link";

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body>
        <header>
          <nav>
            <Link href="/">Home</Link> <Link href="/docs">Docs</Link> <Link href="/blog">Blog</Link>{" "}
            <Link href="/pricing">Pricing</Link> <Link href="/contact">Contact</Link>
          </nav>
        </header>
        {children}
        <noscript><p>This page works without JavaScript.</p></noscript>
        <footer><p>Acme Next, a test site for seo-suite.</p></footer>
      </body>
    </html>
  );
}
