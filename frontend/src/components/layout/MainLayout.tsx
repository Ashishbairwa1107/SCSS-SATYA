import React, { useState } from 'react';
import { Outlet, useNavigate } from 'react-router-dom';
import { Sidebar } from './Sidebar';
import { TopHeader } from './TopHeader';
import { api } from '../../services/api';

export const MainLayout: React.FC = () => {
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);
  const [isGeneratingSpecimen, setIsGeneratingSpecimen] = useState(false);
  const navigate = useNavigate();

  const handleGenerateSpecimen = async (type: 'camera-style' | 'spliced-composite' | 'lossless-png') => {
    try {
      setIsGeneratingSpecimen(true);
      const res = await api.generateSpecimen(type);
      setMobileMenuOpen(false);
      navigate(`/examinations/${res.id}`);
    } catch (err) {
      alert(`Failed to generate specimen: ${err instanceof Error ? err.message : String(err)}`);
    } finally {
      setIsGeneratingSpecimen(false);
    }
  };

  return (
    <div className="flex h-screen overflow-hidden bg-[#F4F6F9] dark:bg-[#0A1220]">
      {/* Desktop Persistent Sidebar */}
      <div className="hidden md:flex md:shrink-0">
        <Sidebar
          onGenerateSpecimen={handleGenerateSpecimen}
          isGeneratingSpecimen={isGeneratingSpecimen}
        />
      </div>

      {/* Mobile Navigation Drawer */}
      {mobileMenuOpen && (
        <div className="fixed inset-0 z-40 md:hidden flex">
          <div
            className="fixed inset-0 bg-black/50 backdrop-blur-xs"
            onClick={() => setMobileMenuOpen(false)}
          />
          <div className="relative flex-1 flex flex-col max-w-xs w-full bg-[#0F1E36]">
            <Sidebar
              onCloseMobile={() => setMobileMenuOpen(false)}
              onGenerateSpecimen={handleGenerateSpecimen}
              isGeneratingSpecimen={isGeneratingSpecimen}
            />
          </div>
        </div>
      )}

      {/* Main Content Area */}
      <div className="flex-1 flex flex-col min-w-0 overflow-hidden">
        <TopHeader onToggleMobileMenu={() => setMobileMenuOpen(true)} />
        <main className="flex-1 overflow-y-auto p-4 md:p-8">
          <div className="max-w-7xl mx-auto">
            <Outlet />
          </div>
        </main>
      </div>
    </div>
  );
};
