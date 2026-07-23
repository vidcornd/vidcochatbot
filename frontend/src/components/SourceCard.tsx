import type { Source } from "../api/chatApi";

type SourceCardProps = {sources: Source[];};

const MAX_VISIBLE_SOURCES = 3;

function getSourceLabel(source: Source): string {
  return source.title || source.source || "Kaynak";
}

function getSourceKey(source: Source): string {
  return `${getSourceLabel(source)}-${source.page ?? "no-page"}`;
}

function deduplicateSources(sources: Source[]): Source[] {
  const seen = new Set<string>();
  const uniqueSources: Source[] = [];

  for (const source of sources) {
    const key = getSourceKey(source);

    if (!seen.has(key)) {
      seen.add(key);
      uniqueSources.push(source);
    }
  }

  return uniqueSources;
}

export function SourceCard({ sources }: SourceCardProps) {
  const uniqueSources = deduplicateSources(sources);
  const visibleSources = uniqueSources.slice(0, MAX_VISIBLE_SOURCES);

   if (visibleSources.length === 0) return null;

  return (
    <div className="sourceList">
      <div className="sourceListTitle">Kaynaklar</div>

      <div className="sourceItems">
        {visibleSources.map((source) => (
          <div key={getSourceKey(source)} className="sourceItem">
            <span className="sourceName">{getSourceLabel(source)}</span>

            {source.page !== null && source.page !== undefined && (
              <span className="sourcePage">s. {source.page}</span>
            )}
          </div>
        ))}
      </div>
    </div>
  );
}