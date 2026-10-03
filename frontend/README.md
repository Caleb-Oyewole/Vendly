# Vendly Frontend

This is the frontend implementation of the Vendly Organizer Dashboard (3-Day Sprint), built with React 19, TypeScript, Vite, Tailwind CSS, and TanStack Query v5.

## Project Structure

- `src/api` - API client and generated OpenAPI types (`schema.d.ts`).
- `src/components` - Shared UI components (AppShell, StatCard, etc.).
- `src/hooks` - React Query hooks for fetching data (e.g. `useEventStatus`, `useEvents`, `useBudget`).
- `src/pages` - Route components (`CreateEventPage`, `EventDashboardPage`, etc.).
- `src/mocks` - Mock fixtures and API handlers for local development.

## Setup and Development

1. Install dependencies:
   ```bash
   npm install
   ```

2. Configure environment variables. Copy `.env.example` to `.env` or set these variables:
   ```env
   VITE_API_URL=http://localhost:8000/api/v1
   VITE_POLL_MS=3000
   VITE_USE_MOCK=false
   ```
   > **Note:** Set `VITE_USE_MOCK=true` to run the UI using mock fixtures when the backend is unavailable.

3. Start the development server:
   ```bash
   npm run dev
   ```

## Backend Integration Details

This frontend has been built strictly to the provided PRD and API contract. 

### CORS Policy (Important for Backend)
Since the frontend and backend are hosted on different domains/ports during development and potentially production, the backend **MUST** configure CORS (Cross-Origin Resource Sharing) correctly.
- **Allowed Origins:** Should include `http://localhost:5173` (Vite's default port) and the production Vercel URL.
- **Allowed Methods:** `GET`, `POST`, `PATCH`, `DELETE`, `OPTIONS`.
- **Allowed Headers:** `Content-Type`, `Accept`.
- **Credentials:** Not required for this hackathon build as there is no authentication.

### Data Types & Conversions
- **Money:** The frontend UI accepts and displays Naira (NGN), but **all monetary amounts sent to and received from the API are in minor units (kobo)**. For example, `NGN 50,000` is sent as `5000000`. The frontend handles division/multiplication by 100 on display/submit.
- **Phone Numbers:** Users may input local phone formats (e.g., `08012345671`). The frontend automatically formats these into E.164 format (`+2348012345671`) before sending to the backend.
- **Dates & Times:** Dates are sent as `YYYY-MM-DD` and times as `HH:MM` (24-hour format).

### API Contract Expectations
All expected API calls and request/response structures map directly to the documented PRD (`/api/v1/events`, `/api/v1/notify/send`, `/api/v1/events/{id}/budget`, etc.). 

The frontend uses `TanStack Query` to poll `GET /api/v1/events/{id}/status?since={version}` every 3 seconds for real-time updates. The backend must respect the `since` query parameter and return `{ changed: false, version: X }` if no updates occurred to prevent unnecessary data over the wire.

For full schema and error shapes (e.g. 422 validations mapping to dotted fields), please refer to the shared Backend Spec PDF.
