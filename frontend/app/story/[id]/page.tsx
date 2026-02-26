import { getStory } from "../../../lib/api";

export default async function StoryPage({ params }: { params: Promise<{ id: string }> }) {
  const { id } = await params;
  const story = await getStory(id);

  return (
    <main>
      <article className="card" style={{ marginBottom: "1rem" }}>
        <h1 style={{ marginTop: 0 }}>{story.headline}</h1>
        <p>{story.long_summary}</p>
        <small>
          {story.primary_category} · {story.status} · updated {new Date(story.last_updated_at).toLocaleString()}
        </small>
      </article>

      <section className="card">
        <h2 style={{ marginTop: 0 }}>Source Links</h2>
        <ul>
          {story.sources.map((source) => (
            <li key={`${source.source_name}-${source.url}`}>
              <a href={source.url} target="_blank" rel="noreferrer">
                {source.source_name}
              </a>{" "}
              ({source.source_type})
            </li>
          ))}
        </ul>
      </section>
    </main>
  );
}
