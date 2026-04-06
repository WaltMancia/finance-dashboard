import {
    ResponsiveContainer, LineChart, Line, XAxis, YAxis,
    CartesianGrid, Tooltip, ReferenceLine,
} from 'recharts';

const CustomTooltip = ({ active, payload, label }) => {
    if (!active || !payload?.length) return null;
    return (
        <div className="bg-white border border-gray-100 rounded-xl shadow-lg p-3">
            <p className="text-sm font-semibold text-gray-900 mb-1">{label}</p>
            <p className="text-sm text-rose-600">
                Gastos: ${payload[0]?.value?.toLocaleString()}
            </p>
        </div>
    );
};

const PredictionChart = ({ data = [], prediction = null }) => {
    if (!data.length) return null;

    const chartData = data.map((d) => ({
        name: d.month_label,
        gastos: d.expenses,
    }));

    // Añadimos el punto de predicción al final
    if (prediction) {
        chartData.push({
            name: 'Predicción',
            gastos: prediction.predicted_total,
            isPrediction: true,
        });
    }

    return (
        <ResponsiveContainer width="100%" height={180}>
            <LineChart data={chartData}>
                <CartesianGrid strokeDasharray="3 3" stroke="#f1f5f9" vertical={false} />
                <XAxis
                    dataKey="name"
                    tick={{ fontSize: 10, fill: '#94a3b8' }}
                    axisLine={false}
                    tickLine={false}
                />
                <YAxis
                    tick={{ fontSize: 10, fill: '#94a3b8' }}
                    axisLine={false}
                    tickLine={false}
                    tickFormatter={(v) => `$${v.toLocaleString()}`}
                />
                <Tooltip content={<CustomTooltip />} />

                {/* ReferenceLine marca el punto donde empieza la predicción */}
                <ReferenceLine
                    x="Predicción"
                    stroke="#94a3b8"
                    strokeDasharray="4 4"
                    label={{ value: 'Predicción', position: 'top', fontSize: 10, fill: '#94a3b8' }}
                />

                <Line
                    type="monotone"
                    dataKey="gastos"
                    stroke="#f43f5e"
                    strokeWidth={2.5}
                    dot={{ fill: '#f43f5e', r: 4 }}
                    // El punto de predicción tiene un estilo diferente
                    activeDot={{ r: 6 }}
                />
            </LineChart>
        </ResponsiveContainer>
    );
};

export default PredictionChart;