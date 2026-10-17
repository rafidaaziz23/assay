import React from 'react';
import { Outlet } from 'react-router-dom';
import { AppSidebar } from '../components/organisms/AppSidebar';
import { AppHeader } from '../components/organisms/AppHeader';

export const AppLayout: React.FC = () => {
  return (
    <div className="min-h-screen bg-[#F8FAFC] text-[#0F172A] flex font-sans antialiased">
      {/* Floating Sidebar */}
      <AppSidebar />

      {/* Main Content Area: Offset by 88px to accommodate detached floating sidebar */}
      <div className="flex-1 flex flex-col min-w-0 pl-[84px]">
        <AppHeader />
        <main className="flex-1 p-6 max-w-7xl w-full mx-auto">
          <Outlet />
        </main>
      </div>
    </div>
  );
};
