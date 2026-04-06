import { NavLink } from 'react-router-dom';
import { useEffect } from 'react';
import { useLocation } from 'react-router-dom';
import {
    LayoutDashboard, ArrowLeftRight, BarChart3,
    Upload, LogOut, TrendingUp, X,
} from 'lucide-react';
import useAuth from '../../hooks/useAuth.js';
import useAuthStore from '../../store/authStore.js';

const navItems = [
    { to: '/', icon: LayoutDashboard, label: 'Dashboard', end: true },
    { to: '/transacciones', icon: ArrowLeftRight, label: 'Transacciones' },
    { to: '/analisis', icon: BarChart3, label: 'Análisis' },
    { to: '/importar', icon: Upload, label: 'Importar CSV' },
];

const Sidebar = ({ open = false, onClose }) => {
    const { handleLogout } = useAuth();
    const { user } = useAuthStore();
    const location = useLocation();

    useEffect(() => {
        onClose?.();
    }, [location.pathname, onClose]);

    return (
        <>
            <div
                className={`fixed inset-0 z-40 bg-black/40 transition-opacity md:hidden ${open ? 'opacity-100' : 'pointer-events-none opacity-0'}`}
                onClick={onClose}
                aria-hidden="true"
            />

            <aside className={`fixed inset-y-0 left-0 z-50 flex h-full w-72 flex-col border-r border-gray-100 bg-white shadow-2xl transition-transform duration-300 md:w-64 md:translate-x-0 md:shadow-none ${open ? 'translate-x-0' : '-translate-x-full md:translate-x-0'}`}>
                <div className="flex items-center justify-between border-b border-gray-100 px-5 py-5">
                    <div className="flex items-center gap-2.5">
                        <div className="flex h-8 w-8 items-center justify-center rounded-xl bg-gray-900">
                            <TrendingUp size={16} className="text-white" />
                        </div>
                        <span className="font-bold text-gray-900">FinanceAI</span>
                    </div>
                    <button
                        type="button"
                        onClick={onClose}
                        className="inline-flex h-9 w-9 items-center justify-center rounded-xl text-gray-500 hover:bg-gray-100 hover:text-gray-700 md:hidden"
                        aria-label="Cerrar menú"
                    >
                        <X size={18} />
                    </button>
                </div>

                <nav className="flex-1 space-y-1 px-3 py-4">
                    {navItems.map(({ to, icon: Icon, label, end }) => (
                        <NavLink
                            key={to}
                            to={to}
                            end={end}
                            onClick={onClose}
                            className={({ isActive }) =>
                                `flex items-center gap-3 rounded-xl px-3 py-2.5 text-sm font-medium transition-colors duration-150 ${isActive
                                    ? 'bg-gray-900 text-white'
                                    : 'text-gray-600 hover:bg-gray-50 hover:text-gray-900'
                                }`
                            }
                        >
                            <Icon size={18} />
                            {label}
                        </NavLink>
                    ))}
                </nav>

                <div className="border-t border-gray-100 px-3 py-4">
                    <div className="mb-1 flex items-center gap-3 px-3 py-2">
                        <div className="flex h-8 w-8 items-center justify-center rounded-full bg-gray-100 text-sm font-semibold text-gray-700">
                            {user?.name?.charAt(0).toUpperCase()}
                        </div>
                        <div className="min-w-0 flex-1">
                            <p className="truncate text-sm font-medium text-gray-900">
                                {user?.name}
                            </p>
                            <p className="truncate text-xs text-gray-400">{user?.email}</p>
                        </div>
                    </div>
                    <button
                        onClick={handleLogout}
                        className="flex w-full items-center gap-3 rounded-xl px-3 py-2.5 text-sm text-gray-600 transition-colors duration-150 hover:bg-red-50 hover:text-red-600"
                    >
                        <LogOut size={16} />
                        Cerrar sesión
                    </button>
                </div>
            </aside>
        </>
    );
};

export default Sidebar;