import Link from "next/link";
import { getCategories, getStories } from "../lib/api";

export default async function HomePage({
  searchParams,
}: {
  searchParams: Promise<{ category?: string }>;
}) {
  const { category } = await searchParams;
  const selectedCategory = category?.trim() || undefined;
  const [stories, categories] = await Promise.all([getStories(selectedCategory), getCategories()]);

  return (
    <main>
      <section className="card" style={{ marginBottom: "1rem" }}>
        <h1 style={{ marginTop: 0 }}>Latest Stories</h1>
        <p style={{ marginBottom: 0 }}>All sources are manually curated by the PulseWire owner.</p>
      </section>

      <section className="card" style={{ marginBottom: "1rem" }}>
        <h2 style={{ marginTop: 0, marginBottom: "0.5rem" }}>Categories</h2>
        <div style={{ display: "flex", gap: "0.5rem", flexWrap: "wrap" }}>
          <Link className="badge" href="/" style={{ textDecoration: "none" }}>
            All
          </Link>
          {categories.map((item) => (
            <Link className="badge" href={`/?category=${item.slug}`} key={item.slug} style={{ textDecoration: "none" }}>
              {item.name}
            </Link>
          ))}
        </div>
      </section>

      <section style={{ display: "grid", gap: "0.75rem" }}>
        {stories.map((story) => (
          (() => {
            const headline = story.headline.trim();
            const summary = story.short_summary.trim();
            const normalizedHeadline = headline.toLowerCase();
            const normalizedSummary = summary.toLowerCase();
            const showsDuplicateSummary =
              normalizedSummary === normalizedHeadline || normalizedSummary.startsWith(`${normalizedHeadline}:`);

            return (
              <article className="card" key={story.id}>
                <h3 style={{ marginTop: 0 }}>
                  <Link href={`/story/${story.id}`}>{story.headline}</Link>
                </h3>
                {!showsDuplicateSummary && summary && <p>{story.short_summary}</p>}
                <small>
                  {story.primary_category} · {story.status} · {story.source_count} sources
                </small>
              </article>
            );
          })()
        ))}
      </section>
    </main>
  );
}
