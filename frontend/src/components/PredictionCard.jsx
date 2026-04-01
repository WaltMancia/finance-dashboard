import { TrendingUp, TrendingDown, Minus, AlertCircle } from 'lucide-react';
import Card, { CardHeader, CardContent } from './ui/Card.jsx';
import PredictionChart from './charts/PredictionChart.jsx';

const trendConfig = {
    up: {
        icon: TrendingUp,
        color: 'text-rose-600',
        bg: 'bg-rose-50',
        label: 'Tendencia al alza',
        description: 'Gastas más que el mes anterior',
    },
    down: {
        icon: TrendingDown,
        color: 'text-emerald-600',
        bg: 'bg-emerald-50',
        label: 'Tendencia a la baja',
        description: 'Gastas menos que el mes anterior',
    },
    stable: {
        icon: Minus,
        color: 'text-blue-600',
        bg: 'bg-blue-50',
        label: 'Tendencia estable',
        description: 'Similar al mes anterior',
    },
};

const confidenceLabel = {
    high: { label: 'Alta confianza', color: 'text-emerald-600' },
    medium: { label: 'Confianza media', color: 'text-amber-600' },
    low: { label: 'Baja confianza', color: 'text-gray-400' },
};

const PredictionCard = ({ prediction }) => {
    if (!prediction) return null;

    const trend = trendConfig[prediction.trend] || trendConfig.stable;
    const confidence = confidenceLabel[prediction.confidence] || confidenceLabel.low;
    const TrendIcon = trend.icon;

    return (
        <Card>
            <CardHeader>
                <div className="flex items-center justify-between">
                    <h3 className="font-semibold text-gray-900">Predicción del mes</h3>
                    <span className={`text-xs font-medium ${confidence.color}`}>
                        {confidence.label}
                    </span>
                </div>
            </CardHeader>

            <CardContent>
                <div className="grid grid-cols-2 gap-4 mb-5">
                    {/* Gastado hasta hoy */}
                    <div className="bg-gray-50 rounded-xl p-4">
                        <p className="text-xs text-gray-500 mb-1">Gastado hasta hoy</p>
                        <p className="text-xl font-bold text-gray-900">
                            ${prediction.current_month_spent.toLocaleString()}
                        </p>
                        <p className="text-xs text-gray-400 mt-0.5">
                            {prediction.days_elapsed} días transcurridos
                        </p>
                    </div>

                    {/* Predicción total */}
                    <div className="bg-rose-50 rounded-xl p-4">
                        <p className="text-xs text-rose-600 mb-1">Predicción total</p>
                        <p className="text-xl font-bold text-rose-700">
                            ${prediction.predicted_total.toLocaleString()}
                        </p>
                        <p className="text-xs text-rose-400 mt-0.5">
                            {prediction.days_remaining} días restantes
                        </p>
                    </div>
                </div>

                {/* Indicador de tendencia */}
                <div className={`flex items-center gap-3 p-3 rounded-xl ${trend.bg} mb-5`}>
                    <div className={`p-2 rounded-lg bg-white`}>
                        <TrendIcon size={16} className={trend.color} />
                    </div>
                    <div>
                        <p className={`text-sm font-semibold ${trend.color}`}>
                            {trend.label} · {prediction.trend_percentage}%
                        </p>
                        <p className="text-xs text-gray-500">{trend.description}</p>
                    </div>
                </div>

                {/* Promedio diario */}
                <div className="flex items-center gap-2 mb-5 text-sm text-gray-600">
                    <AlertCircle size={14} className="text-gray-400 flex-shrink-0" />
                    <span>
                        Promedio diario actual:
                        <span className="font-semibold text-gray-900 ml-1">
                            ${prediction.daily_average.toFixed(2)}
                        </span>
                    </span>
                </div>

                {/* Gráfica de tendencia histórica */}
                <PredictionChart
                    data={prediction.historical_months}
                    prediction={prediction}
                />
            </CardContent>
        </Card>
    );
};

export default PredictionCard;