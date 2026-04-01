import {
    ResponsiveContainer, BarChart, Bar, XAxis, YAxis,
    CartesianGrid, Tooltip, Legend,
} from 'recharts';

// Tooltip personalizado — se renderiza al hacer hover en la gráfica
const CustomTooltip = ({ active, payload, label }) => {
    if (!active || !payload?.length) return null;

    return (
        <div className="bg-white border border-gray-100 rounded-xl shadow-lg p-3">
            <p className="text-sm font-semibold text-gray-900 mb-2">{label}</p>
            {payload.map((entry) => (
                <div key={entry.name} className="flex items-center gap-2 text-sm">
                    <span
                        className="w-2.5 h-2.5 rounded-full"
                        style={{ backgroundColor: entry.color }}
                    />
                    <span className="text-gray-600 capitalize">{entry.name}:</span>
                    <span className="font-medium">${entry.value.toLocaleString()}</span>
                </div>
            ))}
        </div>
    );
};

const MonthlyTrendChart = ({ data = [] }) => {
    if (!data.length) return (
        <div className="h-64 flex items-center justify-center text-gray-400 text-sm">
            Sin datos suficientes para mostrar la tendencia
        </div>
    );

    // Recharts necesita que las claves sean en inglés para dataKey
    // pero mostramos labels en español con el formatter
    const formattedData = data.map((d) => ({
        name: d.month_label,
        Ingresos: d.income,
        Gastos: d.expenses,
    }));

    return (
        // ResponsiveContainer hace la gráfica responsiva automáticamente
        // width="100%" → toma todo el ancho del contenedor padre
        // height={280} → altura fija en píxeles
        <ResponsiveContainer width="100%" height={280}>
            <BarChart data={formattedData} barGap={4}>
                <CartesianGrid
                    strokeDasharray="3 3"
                    stroke="#f1f5f9"
                    vertical={false}  // Solo líneas horizontales — más limpio
                />
                <XAxis
                    dataKey="name"
                    tick={{ fontSize: 12, fill: '#94a3b8' }}
                    axisLine={false}
                    tickLine={false}
                />
                <YAxis
                    tick={{ fontSize: 12, fill: '#94a3b8' }}
                    axisLine={false}
                    tickLine={false}
                    tickFormatter={(v) => `$${v.toLocaleString()}`}
                />
                <Tooltip content={<CustomTooltip />} />
                <Legend
                    wrapperStyle={{ fontSize: '12px', paddingTop: '16px' }}
                />
                <Bar dataKey="Ingresos" fill="#10b981" radius={[6, 6, 0, 0]} />
                <Bar dataKey="Gastos" fill="#f43f5e" radius={[6, 6, 0, 0]} />
            </BarChart>
        </ResponsiveContainer>
    );
};

export default MonthlyTrendChart;