import { RefreshCw } from 'lucide-react';
import useDashboard from '../../hooks/useDashboard.js';
import useAuthStore from '../../store/authStore.js';
import SummaryCards from '../../components/SummaryCards.jsx';
import PredictionCard from '../../components/PredictionCard.jsx';
import MonthlyTrendChart from '../../components/charts/MonthlyTrendChart.jsx';
import CategoryPieChart from '../../components/charts/CategoryPieChart.jsx';
import Card, { CardHeader, CardContent } from '../../components/ui/Card.jsx';
import Spinner from '../../components/ui/Spinner.jsx';
import Button from '../../components/ui/Button.jsx';
import EmptyState from '../../components/ui/EmptyState.jsx';
import { Link } from 'react-router-dom';

const DashboardPage = () => {
    const { user } = useAuthStore();
    const { data, loading, error, refetch } = useDashboard();

    if (loading) return (
        <div className="flex items-center justify-center min-h-96">
            <Spinner size="lg" />
        </div>
    );

    if (error) return (
        <div className="flex items-center justify-center min-h-96">
            <EmptyState
                icon="⚠️"
                title="Error al cargar"
                description={error}
                action={<Button onClick={refetch}>Reintentar</Button>}
            />
        </div>
    );

    const hasData = data?.summary?.transaction_count > 0;

    return (
        <div className="space-y-6">
            {/* Header */}
            <div className="flex items-center justify-between">
                <div>
                    <h1 className="text-2xl font-bold text-gray-900">
                        Buenos días, {user?.name?.split(' ')[0]} 👋
                    </h1>
                    <p className="text-gray-500 text-sm mt-0.5">
                        Aquí está el resumen de tus finanzas
                    </p>
                </div>
                <Button variant="secondary" size="sm" onClick={refetch}>
                    <RefreshCw size={15} />
                    Actualizar
                </Button>
            </div>

            {!hasData ? (
                <EmptyState
                    icon="💰"
                    title="Aún no tienes transacciones"
                    description="Añade tu primera transacción o importa un CSV para ver tus análisis"
                    action={
                        <div className="flex gap-3">
                            <Link to="/transacciones">
                                <Button>Añadir transacción</Button>
                            </Link>
                            <Link to="/importar">
                                <Button variant="secondary">Importar CSV</Button>
                            </Link>
                        </div>
                    }
                />
            ) : (
                <>
                    {/* Tarjetas de resumen */}
                    <SummaryCards
                        summary={data.summary}
                        comparison={data.comparison}
                    />

                    {/* Gráficas principales */}
                    <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                        {/* Tendencia mensual */}
                        <Card>
                            <CardHeader>
                                <h3 className="font-semibold text-gray-900">
                                    Tendencia mensual
                                </h3>
                                <p className="text-sm text-gray-400 mt-0.5">
                                    Ingresos y gastos de los últimos 6 meses
                                </p>
                            </CardHeader>
                            <CardContent>
                                <MonthlyTrendChart data={data.monthly_trend} />
                            </CardContent>
                        </Card>

                        {/* Distribución por categoría */}
                        <Card>
                            <CardHeader>
                                <h3 className="font-semibold text-gray-900">
                                    Gastos por categoría
                                </h3>
                                <p className="text-sm text-gray-400 mt-0.5">
                                    Distribución del mes actual
                                </p>
                            </CardHeader>
                            <CardContent>
                                <CategoryPieChart data={data.category_breakdown} />
                            </CardContent>
                        </Card>
                    </div>

                    {/* Predicción y comparativa */}
                    <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                        {/* Predicción */}
                        <PredictionCard prediction={data.prediction} />

                        {/* Comparativa mes anterior */}
                        <Card>
                            <CardHeader>
                                <h3 className="font-semibold text-gray-900">
                                    Comparativa mensual
                                </h3>
                                <p className="text-sm text-gray-400 mt-0.5">
                                    Este mes vs mes anterior
                                </p>
                            </CardHeader>
                            <CardContent>
                                {data.comparison && (
                                    <div className="space-y-4">
                                        {/* Gastos */}
                                        <div className="flex items-center justify-between p-3
                      bg-gray-50 rounded-xl">
                                            <span className="text-sm text-gray-600">Gastos</span>
                                            <div className="text-right">
                                                <p className="font-semibold text-gray-900">
                                                    ${data.comparison.current_month.expenses.toLocaleString()}
                                                </p>
                                                <p className={`text-xs ${data.comparison.expense_change >= 0
                                                    ? 'text-rose-500' : 'text-emerald-500'}`}>
                                                    {data.comparison.expense_change >= 0 ? '+' : ''}
                                                    {data.comparison.expense_change_percentage}% vs anterior
                                                </p>
                                            </div>
                                        </div>

                                        {/* Ingresos */}
                                        <div className="flex items-center justify-between p-3
                      bg-gray-50 rounded-xl">
                                            <span className="text-sm text-gray-600">Ingresos</span>
                                            <div className="text-right">
                                                <p className="font-semibold text-gray-900">
                                                    ${data.comparison.current_month.income.toLocaleString()}
                                                </p>
                                                <p className={`text-xs ${data.comparison.income_change >= 0
                                                    ? 'text-emerald-500' : 'text-rose-500'}`}>
                                                    {data.comparison.income_change >= 0 ? '+' : ''}
                                                    {data.comparison.income_change_percentage}% vs anterior
                                                </p>
                                            </div>
                                        </div>

                                        {/* Top aumentos */}
                                        {data.comparison.top_increases?.length > 0 && (
                                            <div>
                                                <p className="text-xs font-medium text-gray-500
                          uppercase tracking-wide mb-2">
                                                    Mayores aumentos
                                                </p>
                                                <div className="space-y-2">
                                                    {data.comparison.top_increases.map((cat) => (
                                                        <div key={cat.category_name}
                                                            className="flex items-center justify-between text-sm">
                                                            <span className="flex items-center gap-1.5">
                                                                <span>{cat.category_icon}</span>
                                                                <span className="text-gray-700">{cat.category_name}</span>
                                                            </span>
                                                            <span className="text-rose-600 font-medium">
                                                                +${cat.change?.toFixed(2)}
                                                            </span>
                                                        </div>
                                                    ))}
                                                </div>
                                            </div>
                                        )}
                                    </div>
                                )}
                            </CardContent>
                        </Card>
                    </div>
                </>
            )}
        </div>
    );
};

export default DashboardPage;