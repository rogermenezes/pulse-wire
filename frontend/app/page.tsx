import Link from "next/link";
import { getCategories, getLatestStories } from "../lib/api";

export default async function HomePage() {
  const [stories, categories] = await Promise.all([getLatestStories(), getCategories()]);

  return (
    <main>
      <section className="card" style={{ marginBottom: "1rem" }}>
        <h1 style={{ marginTop: 0 }}>Latest Stories</h1>
        <p style={{ marginBottom: 0 }}>All sources are manually curated by the PulseWire owner.</p>
      </section>

      <section className="card" style={{ marginBottom: "1rem" }}>
        <h2 style={{ marginTop: 0, marginBottom: "0.5rem" }}>Categories</h2>
        <div style={{ display: "flex", gap: "0.5rem", flexWrap: "wrap" }}>
          {categories.map((category) => (
            <span className="badge" key={category}>
              {category}
            </span>
          ))}
        </div>
      </section>

      <section style={{ display: "grid", gap: "0.75rem" }}>
        {stories.map((story) => (
          <article className="card" key={story.id}>
            <h3 style={{ marginTop: 0 }}>
              <Link href={`/story/${story.id}`}>{story.headline}</Link>
            </h3>
            <p>{story.short_summary}</p>
            <small>
              {story.primary_category} · {story.status} · {story.source_count} sources
            </small>
          </article>
        ))}
      </section>
    </main>
  );
}
