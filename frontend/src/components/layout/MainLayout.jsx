import { useState } from 'react';
import { Menu } from 'lucide-react';
import { Outlet } from 'react-router-dom';
import Sidebar from './Sidebar.jsx';

const MainLayout = () => {
    const [sidebarOpen, setSidebarOpen] = useState(false);

    return (
        <div className="min-h-screen bg-gray-50 md:pl-64">
            <Sidebar open={sidebarOpen} onClose={() => setSidebarOpen(false)} />

            <header className="sticky top-0 z-20 flex items-center gap-3 border-b border-gray-200 bg-white/95 px-4 py-3 backdrop-blur md:hidden">
                <button
                    type="button"
                    onClick={() => setSidebarOpen(true)}
                    className="inline-flex h-10 w-10 items-center justify-center rounded-xl border border-gray-200 text-gray-700"
                    aria-label="Abrir menú"
                >
                    <Menu size={18} />
                </button>
                <div>
                    <p className="text-sm font-semibold text-gray-900">FinanceAI</p>
                    <p className="text-xs text-gray-500">Panel de finanzas</p>
                </div>
            </header>

            <main className="px-4 py-5 sm:px-6 lg:px-8 lg:py-8">
                <div className="mx-auto w-full max-w-6xl">
                    <Outlet />
                </div>
            </main>
        </div>
    );
};

export default MainLayout;