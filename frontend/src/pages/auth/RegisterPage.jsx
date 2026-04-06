import { useState } from 'react';
import { Link } from 'react-router-dom';
import { TrendingUp, User, Mail, Lock } from 'lucide-react';
import useAuth from '../../hooks/useAuth.js';
import Button from '../../components/ui/Button.jsx';

const RegisterPage = () => {
    const [form, setForm] = useState({ name: '', email: '', password: '' });
    const { register, loading } = useAuth();

    const handleSubmit = async (e) => {
        e.preventDefault();
        await register(form);
    };

    const fields = [
        { key: 'name', label: 'Nombre completo', type: 'text', icon: User, placeholder: 'Juan Pérez' },
        { key: 'email', label: 'Correo electrónico', type: 'email', icon: Mail, placeholder: 'tu@email.com' },
        { key: 'password', label: 'Contraseña', type: 'password', icon: Lock, placeholder: '••••••••' },
    ];

    return (
        <div className="min-h-screen flex items-center justify-center bg-gray-50 px-4 py-8">
            <div className="w-full max-w-md">
                <div className="text-center mb-8">
                    <div className="inline-flex items-center gap-2 mb-4">
                        <div className="w-9 h-9 bg-gray-900 rounded-xl flex items-center justify-center">
                            <TrendingUp size={18} className="text-white" />
                        </div>
                        <span className="font-bold text-gray-900 text-lg">FinanceAI</span>
                    </div>
                    <h2 className="text-2xl font-bold text-gray-900">Crea tu cuenta</h2>
                    <p className="text-gray-500 mt-1 text-sm">Empieza a controlar tus finanzas hoy</p>
                </div>

                <div className="bg-white rounded-2xl border border-gray-100 shadow-sm p-8">
                    <form onSubmit={handleSubmit} className="space-y-4">
                        {fields.map(({ key, label, type, icon: Icon, placeholder }) => (
                            <div key={key}>
                                <label className="block text-sm font-medium text-gray-700 mb-1.5">
                                    {label}
                                </label>
                                <div className="relative">
                                    <Icon size={16} className="absolute left-3.5 top-1/2
                    -translate-y-1/2 text-gray-400" />
                                    <input
                                        type={type}
                                        value={form[key]}
                                        onChange={(e) => setForm({ ...form, [key]: e.target.value })}
                                        required
                                        minLength={key === 'password' ? 6 : undefined}
                                        placeholder={placeholder}
                                        className="w-full pl-10 pr-4 py-2.5 border border-gray-200
                      rounded-xl text-sm focus:outline-none focus:ring-2
                      focus:ring-gray-900 focus:border-transparent"
                                    />
                                </div>
                            </div>
                        ))}

                        <Button type="submit" loading={loading} className="w-full mt-2" size="lg">
                            Crear cuenta gratuita
                        </Button>
                    </form>
                </div>

                <p className="text-center text-sm text-gray-500 mt-4">
                    ¿Ya tienes cuenta?{' '}
                    <Link to="/login" className="font-medium text-gray-900 hover:underline">
                        Inicia sesión
                    </Link>
                </p>
            </div>
        </div>
    );
};

export default RegisterPage;