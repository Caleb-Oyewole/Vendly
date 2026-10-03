import { Link } from 'react-router-dom';

export default function NotFoundPage() {
  return (
    <div className="py-12 text-center">
      <h2 className="text-xl font-semibold text-ink">Page not found</h2>
      <Link to="/" className="mt-4 inline-block text-sm text-brand underline">
        Back to events
      </Link>
    </div>
  );
}
