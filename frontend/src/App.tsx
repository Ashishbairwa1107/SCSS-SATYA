import React from 'react';
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { ThemeProvider } from './context/ThemeContext';
import { MainLayout } from './components/layout/MainLayout';
import { DashboardPage } from './pages/DashboardPage';
import { NewExaminationPage } from './pages/NewExaminationPage';
import { ExaminationDetailPage } from './pages/ExaminationDetailPage';
import { EvidenceVaultPage } from './pages/EvidenceVaultPage';
import { MethodologyPage } from './pages/MethodologyPage';
import { SystemInfoPage } from './pages/SystemInfoPage';

export const App: React.FC = () => {
  return (
    <ThemeProvider>
      <BrowserRouter>
        <Routes>
          <Route path="/" element={<MainLayout />}>
            <Route index element={<DashboardPage />} />
            <Route path="new" element={<NewExaminationPage />} />
            <Route path="examinations/:id" element={<ExaminationDetailPage />} />
            <Route path="vault" element={<EvidenceVaultPage />} />
            <Route path="methodology" element={<MethodologyPage />} />
            <Route path="system" element={<SystemInfoPage />} />
            <Route path="*" element={<Navigate to="/" replace />} />
          </Route>
        </Routes>
      </BrowserRouter>
    </ThemeProvider>
  );
};
