import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import toast from 'react-hot-toast';
import useAuthStore from '../store/authStore.js';
import { loginService, registerService } from '../services/auth.service.js';

const useAuth = () => {
    const [loading, setLoading] = useState(false);
    const { setAuth, logout } = useAuthStore();
    const navigate = useNavigate();

    const login = async (credentials) => {
        setLoading(true);
        try {
            const data = await loginService(credentials);
            setAuth(data.user, data.access_token, data.refresh_token);
            toast.success(`¡Bienvenido, ${data.user.name}!`);
            navigate('/');
        } catch (error) {
            toast.error(error.response?.data?.detail || 'Error al iniciar sesión');
        } finally {
            setLoading(false);
        }
    };

    const register = async (userData) => {
        setLoading(true);
        try {
            const data = await registerService(userData);
            setAuth(data.user, data.access_token, data.refresh_token);
            toast.success('¡Cuenta creada exitosamente!');
            navigate('/');
        } catch (error) {
            toast.error(error.response?.data?.detail || 'Error al registrarse');
        } finally {
            setLoading(false);
        }
    };

    const handleLogout = () => {
        logout();
        toast.success('Sesión cerrada');
        navigate('/login');
    };

    return { login, register, handleLogout, loading };
};

export default useAuth;