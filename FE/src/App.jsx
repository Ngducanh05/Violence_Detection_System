import { BrowserRouter, Routes, Route } from 'react-router-dom';
import { Toaster } from 'react-hot-toast';
import MainLayout from './layouts/MainLayout';

import Dashboard from './pages/Dashboard';
import DetectPage from './pages/DetectPage';
import LivePage from './pages/LivePage';
import AuditPage from './pages/AuditPage';
import UserPage from './pages/UserPage';
import LoginPage from './pages/LoginPage'; // Mới
import RegisterPage from './pages/RegisterPage'; // Mới

function App() {
  return (
    <BrowserRouter>
      <Toaster position="top-center" reverseOrder={false} />
      <Routes>
        {/* Các trang nằm TRONG khung giao diện chính (Sidebar + Navbar) */}
        <Route path="/" element={<MainLayout />}>
          <Route index element={<Dashboard />} />
          <Route path="dashboard" element={<Dashboard />} />
          <Route path="live" element={<LivePage />} />
          <Route path="detect" element={<DetectPage />} />
          <Route path="audit" element={<AuditPage />} />
          <Route path="users" element={<UserPage />} />
        </Route>

        {/* Các trang nằm NGOÀI khung giao diện (Full màn hình) */}
        <Route path="/login" element={<LoginPage />} />
        <Route path="/register" element={<RegisterPage />} />
      </Routes>
    </BrowserRouter>
  );
}

export default App;