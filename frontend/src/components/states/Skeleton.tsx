

export default function Skeleton({ rows = 3 }: { rows?: number }) {
  return (
    <div className="space-y-4 animate-pulse">
      {Array(rows).fill(0).map((_, i) => (
        <div key={i} className="h-24 bg-line rounded-card w-full"></div>
      ))}
    </div>
  );
}
