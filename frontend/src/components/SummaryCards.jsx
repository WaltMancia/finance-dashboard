import { TrendingUp, TrendingDown, Wallet, ArrowUpRight, ArrowDownRight } from 'lucide-react';
import Card, { CardContent } from './ui/Card.jsx';

const MetricCard = ({ title, value, icon: Icon, color, change, changeLabel }) => (
    <Card className="hover:shadow-md transition-shadow duration-300">
        <CardContent className="pt-6">
            <div className="flex items-start justify-between">
                <div>
                    <p className="text-sm text-gray-500 font-medium">{title}</p>
                    <p className={`text-2xl font-bold mt-1 ${color}`}>
                        ${value?.toLocaleString('es', { minimumFractionDigits: 2 }) ?? '0.00'}
                    </p>
                </div>
                <div className={`p-2.5 rounded-xl ${color === 'text-emerald-600'
                    ? 'bg-emerald-50' : color === 'text-rose-600'
                        ? 'bg-rose-50' : 'bg-blue-50'}`}>
                    <Icon size={20} className={color} />
                </div>
            </div>

            {change !== undefined && (
                <div className={`flex items-center gap-1 mt-3 text-xs font-medium
          ${change >= 0 ? 'text-emerald-600' : 'text-rose-600'}`}>
                    {change >= 0
                        ? <ArrowUpRight size={14} />
                        : <ArrowDownRight size={14} />
                    }
                    {Math.abs(change)}% {changeLabel}
                </div>
            )}
        </CardContent>
    </Card>
);

const SummaryCards = ({ summary, comparison }) => {
    const expenseChangePct = comparison?.expense_change_percentage ?? 0;
    const incomeChangePct = comparison?.income_change_percentage ?? 0;

    return (
        <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
            <MetricCard
                title="Balance Total"
                value={summary?.balance}
                icon={Wallet}
                color={summary?.balance >= 0 ? 'text-blue-600' : 'text-rose-600'}
            />
            <MetricCard
                title="Total Ingresos"
                value={summary?.total_income}
                icon={TrendingUp}
                color="text-emerald-600"
                change={incomeChangePct}
                changeLabel="vs mes anterior"
            />
            <MetricCard
                title="Total Gastos"
                value={summary?.total_expenses}
                icon={TrendingDown}
                color="text-rose-600"
                change={expenseChangePct}
                changeLabel="vs mes anterior"
            />
        </div>
    );
};

export default SummaryCards;