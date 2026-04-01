import { Routes, Route, Navigate } from 'react-router-dom';
import MainLayout from './components/layout/MainLayout.jsx';
import ProtectedRoute from './components/ProtectedRoute.jsx';
import LoginPage from './pages/auth/LoginPage.jsx';
import RegisterPage from './pages/auth/RegisterPage.jsx';
import DashboardPage from './pages/dashboard/DashboardPage.jsx';
import TransactionsPage from './pages/transactions/TransactionsPage.jsx';
import AnalyticsPage from './pages/analytics/AnalyticsPage.jsx';
import ImportPage from './pages/import/ImportPage.jsx';

const App = () => (
  <Routes>
    <Route path="/login" element={<LoginPage />} />
    <Route path="/registro" element={<RegisterPage />} />

    <Route element={
      <ProtectedRoute>
        <MainLayout />
      </ProtectedRoute>
    }>
      <Route path="/" element={<DashboardPage />} />
      <Route path="/transacciones" element={<TransactionsPage />} />
      <Route path="/analisis" element={<AnalyticsPage />} />
      <Route path="/importar" element={<ImportPage />} />
    </Route>

    <Route path="*" element={<Navigate to="/" replace />} />
  </Routes>
);

export default App;