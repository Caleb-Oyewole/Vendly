import { createBrowserRouter } from 'react-router-dom';
import AppShell from './components/AppShell';
import EventsListPage from './pages/EventsListPage';
import CreateEventPage from './pages/CreateEventPage';
import EventDashboardPage from './pages/EventDashboardPage';
import EventBudgetPage from './pages/EventBudgetPage';
import NotFoundPage from './pages/NotFoundPage';
import LoginPage from './pages/LoginPage';
import ProtectedRoute from './components/ProtectedRoute';

export const router = createBrowserRouter([
  {
    path: '/login',
    element: <LoginPage />
  },
  {
    path: '/',
    element: (
      <ProtectedRoute>
        <AppShell />
      </ProtectedRoute>
    ),
    errorElement: <NotFoundPage />,
    children: [
      {
        index: true,
        element: <EventsListPage />,
      },
      {
        path: 'events/new',
        element: <CreateEventPage />,
      },
      {
        path: 'events/:id',
        element: <EventDashboardPage />,
      },
      {
        path: 'events/:id/budget',
        element: <EventBudgetPage />,
      }
    ],
  },
]);
