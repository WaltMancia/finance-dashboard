import { useState, useEffect } from 'react';
import { Calendar } from 'lucide-react';
import {
    getDashboardService,
    getCategoryBreakdownService,
} from '../../services/analytics.service.js';
import Card, { CardHeader, CardContent } from '../../components/ui/Card.jsx';
import Spinner from '../../components/ui/Spinner.jsx';
import MonthlyTrendChart from '../../components/charts/MonthlyTrendChart.jsx';
import CategoryPieChart from '../../components/charts/CategoryPieChart.jsx';
import PredictionCard from '../../components/PredictionCard.jsx';
import EmptyState from '../../components/ui/EmptyState.jsx';
import { Link } from 'react-router-dom';
import Button from '../../components/ui/Button.jsx';

const AnalyticsPage = () => {
    const [data, setData] = useState(null);
    const [loading, setLoading] = useState(true);
    const [selectedMonth, setSelectedMonth] = useState('');
    const [categoryData, setCategoryData] = useState([]);

    useEffect(() => {
        getDashboardService()
            .then(setData)
            .catch(() => { })
            .finally(() => setLoading(false));
    }, []);

    // Recargamos el desglose por categoría cuando cambia el mes seleccionado
    useEffect(() => {
        getCategoryBreakdownService(selectedMonth || null)
            .then(setCategoryData)
            .catch(() => { });
    }, [selectedMonth]);

    if (loading) return (
        <div className="flex justify-center py-20"><Spinner size="lg" /></div>
    );

    if (!data?.summary?.transaction_count) return (
        <EmptyState
            icon="📊"
            title="Sin datos para analizar"
            description="Añade transacciones para ver tus análisis financieros"
            action={
                <Link to="/transacciones">
                    <Button>Ir a transacciones</Button>
                </Link>
            }
        />
    );

    // Genera las opciones de meses disponibles desde el historial
    const availableMonths = data.monthly_trend.map((m) => ({
        value: m.month,
        label: m.month_label,
    }));

    return (
        <div className="space-y-6">
            <div>
                <h1 className="text-2xl font-bold text-gray-900">Análisis Financiero</h1>
                <p className="text-gray-500 text-sm mt-0.5">
                    Patrones y tendencias de tus finanzas
                </p>
            </div>

            {/* Tendencia de 6 meses */}
            <Card>
                <CardHeader>
                    <h3 className="font-semibold text-gray-900">Tendencia mensual</h3>
                    <p className="text-sm text-gray-400 mt-0.5">
                        Ingresos y gastos de los últimos 6 meses
                    </p>
                </CardHeader>
                <CardContent>
                    <MonthlyTrendChart data={data.monthly_trend} />
                </CardContent>
            </Card>

            {/* Desglose por categoría con filtro de mes */}
            <Card>
                <CardHeader>
                    <div className="flex items-center justify-between">
                        <div>
                            <h3 className="font-semibold text-gray-900">
                                Gastos por categoría
                            </h3>
                            <p className="text-sm text-gray-400 mt-0.5">
                                Distribución de tus gastos
                            </p>
                        </div>

                        {/* Selector de mes */}
                        <div className="flex items-center gap-2">
                            <Calendar size={15} className="text-gray-400" />
                            <select
                                value={selectedMonth}
                                onChange={(e) => setSelectedMonth(e.target.value)}
                                className="border border-gray-200 rounded-xl px-3 py-1.5
                  text-sm focus:outline-none focus:ring-2 focus:ring-gray-900
                  bg-white"
                            >
                                <option value="">Todos los meses</option>
                                {availableMonths.map((m) => (
                                    <option key={m.value} value={m.value}>{m.label}</option>
                                ))}
                            </select>
                        </div>
                    </div>
                </CardHeader>
                <CardContent>
                    <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                        <CategoryPieChart data={categoryData} />

                        {/* Tabla de desglose */}
                        <div className="space-y-2">
                            {categoryData.slice(0, 6).map((cat) => (
                                <div key={cat.category_name}
                                    className="flex items-center gap-3">
                                    <span className="text-lg w-7 text-center">{cat.category_icon}</span>
                                    <div className="flex-1 min-w-0">
                                        <div className="flex items-center justify-between mb-1">
                                            <span className="text-sm font-medium text-gray-700 truncate">
                                                {cat.category_name}
                                            </span>
                                            <span className="text-sm font-semibold text-gray-900 ml-2">
                                                ${cat.total.toLocaleString()}
                                            </span>
                                        </div>
                                        {/* Barra de progreso */}
                                        <div className="h-1.5 bg-gray-100 rounded-full overflow-hidden">
                                            <div
                                                className="h-full rounded-full transition-all duration-500"
                                                style={{
                                                    width: `${cat.percentage}%`,
                                                    backgroundColor: cat.category_color,
                                                }}
                                            />
                                        </div>
                                    </div>
                                    <span className="text-xs text-gray-400 w-10 text-right">
                                        {cat.percentage}%
                                    </span>
                                </div>
                            ))}
                        </div>
                    </div>
                </CardContent>
            </Card>

            {/* Predicción */}
            <PredictionCard prediction={data.prediction} />
        </div>
    );
};

export default AnalyticsPage;