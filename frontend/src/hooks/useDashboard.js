import { useState, useEffect } from 'react';
import { getDashboardService } from '../services/analytics.service.js';
import useAuthStore from '../store/authStore.js';

const useDashboard = () => {
    const [data, setData] = useState(null);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);
    const { user } = useAuthStore();

    useEffect(() => {
        if (!user) return;
        fetchDashboard();
    }, [user]);

    const fetchDashboard = async () => {
        setLoading(true);
        setError(null);
        try {
            const result = await getDashboardService();
            setData(result);
        } catch {
            setError('Error al cargar el dashboard');
        } finally {
            setLoading(false);
        }
    };

    return { data, loading, error, refetch: fetchDashboard };
};

export default useDashboard;