import { NavLink } from 'react-router-dom';
import {
    LayoutDashboard, ArrowLeftRight, BarChart3,
    Upload, LogOut, TrendingUp,
} from 'lucide-react';
import useAuth from '../../hooks/useAuth.js';
import useAuthStore from '../../store/authStore.js';

const navItems = [
    { to: '/', icon: LayoutDashboard, label: 'Dashboard', end: true },
    { to: '/transacciones', icon: ArrowLeftRight, label: 'Transacciones' },
    { to: '/analisis', icon: BarChart3, label: 'Análisis' },
    { to: '/importar', icon: Upload, label: 'Importar CSV' },
];

const Sidebar = () => {
    const { handleLogout } = useAuth();
    const { user } = useAuthStore();

    return (
        <aside className="w-64 min-h-screen bg-white border-r border-gray-100
      flex flex-col fixed left-0 top-0 z-30">

            {/* Logo */}
            <div className="px-6 py-5 border-b border-gray-100">
                <div className="flex items-center gap-2.5">
                    <div className="w-8 h-8 bg-gray-900 rounded-xl flex items-center justify-center">
                        <TrendingUp size={16} className="text-white" />
                    </div>
                    <span className="font-bold text-gray-900">FinanceAI</span>
                </div>
            </div>

            {/* Navegación */}
            <nav className="flex-1 px-3 py-4 space-y-1">
                {navItems.map(({ to, icon: Icon, label, end }) => (
                    <NavLink
                        key={to}
                        to={to}
                        end={end}
                        className={({ isActive }) =>
                            `flex items-center gap-3 px-3 py-2.5 rounded-xl text-sm
              font-medium transition-colors duration-150
              ${isActive
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

            {/* Usuario y logout */}
            <div className="px-3 py-4 border-t border-gray-100">
                <div className="flex items-center gap-3 px-3 py-2 mb-1">
                    <div className="w-8 h-8 bg-gray-100 rounded-full flex items-center
            justify-center text-sm font-semibold text-gray-700">
                        {user?.name?.charAt(0).toUpperCase()}
                    </div>
                    <div className="flex-1 min-w-0">
                        <p className="text-sm font-medium text-gray-900 truncate">
                            {user?.name}
                        </p>
                        <p className="text-xs text-gray-400 truncate">{user?.email}</p>
                    </div>
                </div>
                <button
                    onClick={handleLogout}
                    className="w-full flex items-center gap-3 px-3 py-2.5 rounded-xl
            text-sm text-gray-600 hover:bg-red-50 hover:text-red-600
            transition-colors duration-150"
                >
                    <LogOut size={16} />
                    Cerrar sesión
                </button>
            </div>
        </aside>
    );
};

export default Sidebar;