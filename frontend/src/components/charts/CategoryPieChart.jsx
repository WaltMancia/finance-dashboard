import {
    ResponsiveContainer, PieChart, Pie, Cell,
    Tooltip, Legend,
} from 'recharts';

const CustomTooltip = ({ active, payload }) => {
    if (!active || !payload?.length) return null;
    const item = payload[0].payload;

    return (
        <div className="bg-white border border-gray-100 rounded-xl shadow-lg p-3">
            <div className="flex items-center gap-2 mb-1">
                <span className="text-lg">{item.category_icon}</span>
                <span className="font-semibold text-gray-900 text-sm">
                    {item.category_name}
                </span>
            </div>
            <p className="text-sm text-gray-600">
                ${item.total.toLocaleString()}
                <span className="text-gray-400 ml-1">({item.percentage}%)</span>
            </p>
        </div>
    );
};

// Label personalizado dentro de cada sector del pie
const CustomLabel = ({ cx, cy, midAngle, innerRadius, outerRadius, percentage }) => {
    if (percentage < 5) return null; // No mostramos labels muy pequeños

    const RADIAN = Math.PI / 180;
    const radius = innerRadius + (outerRadius - innerRadius) * 0.5;
    const x = cx + radius * Math.cos(-midAngle * RADIAN);
    const y = cy + radius * Math.sin(-midAngle * RADIAN);

    return (
        <text
            x={x} y={y}
            fill="white"
            textAnchor="middle"
            dominantBaseline="central"
            fontSize={11}
            fontWeight={600}
        >
            {`${percentage}%`}
        </text>
    );
};

const CategoryPieChart = ({ data = [] }) => {
    if (!data.length) return (
        <div className="h-64 flex items-center justify-center text-gray-400 text-sm">
            Sin gastos registrados
        </div>
    );

    // Tomamos solo el top 6 para no saturar la gráfica
    const chartData = data.slice(0, 6);

    return (
        <ResponsiveContainer width="100%" height={300}>
            <PieChart>
                <Pie
                    data={chartData}
                    cx="50%"
                    cy="50%"
                    outerRadius={92}
                    innerRadius={54}
                    dataKey="total"
                    labelLine={false}
                    label={CustomLabel}
                >
                    {/* Cell aplica el color de cada categoría */}
                    {chartData.map((entry, index) => (
                        <Cell
                            key={`cell-${index}`}
                            fill={entry.category_color}
                        />
                    ))}
                </Pie>
                <Tooltip content={<CustomTooltip />} />
                <Legend
                    verticalAlign="bottom"
                    align="center"
                    iconSize={10}
                    height={56}
                    formatter={(_, entry) => (
                        <span style={{ fontSize: '12px', color: '#374151' }}>
                            {entry.payload.category_icon} {entry.payload.category_name}
                        </span>
                    )}
                />
            </PieChart>
        </ResponsiveContainer>
    );
};

export default CategoryPieChart;