import { useState, useEffect, useCallback } from 'react';
import { Plus, Search, Filter, Trash2, Pencil, X } from 'lucide-react';
import {
    getTransactionsService,
    deleteTransactionService,
} from '../../services/transaction.service.js';
import { getCategoriesService } from '../../services/category.service.js';
import Button from '../../components/ui/Button.jsx';
import Badge from '../../components/ui/Badge.jsx';
import Spinner from '../../components/ui/Spinner.jsx';
import EmptyState from '../../components/ui/EmptyState.jsx';
import Card from '../../components/ui/Card.jsx';
import TransactionModal from './TransactionModal.jsx';
import toast from 'react-hot-toast';

const typeLabel = { income: 'Ingreso', expense: 'Gasto' };

const TransactionsPage = () => {
    const [transactions, setTransactions] = useState([]);
    const [pagination, setPagination] = useState(null);
    const [categories, setCategories] = useState([]);
    const [loading, setLoading] = useState(true);
    const [deletingId, setDeletingId] = useState(null);
    const [showModal, setShowModal] = useState(false);
    const [editingTransaction, setEditingTransaction] = useState(null);

    // Filtros
    const [search, setSearch] = useState('');
    const [searchInput, setSearchInput] = useState('');
    const [typeFilter, setTypeFilter] = useState('');
    const [categoryFilter, setCategoryFilter] = useState('');
    const [page, setPage] = useState(1);

    const fetchTransactions = useCallback(async () => {
        setLoading(true);
        try {
            const params = { page, limit: 15 };
            if (search) params.search = search;
            if (typeFilter) params.type = typeFilter;
            if (categoryFilter) params.category_id = categoryFilter;

            const data = await getTransactionsService(params);
            setTransactions(data.data);
            setPagination(data.pagination);
        } catch {
            toast.error('Error al cargar transacciones');
        } finally {
            setLoading(false);
        }
    }, [page, search, typeFilter, categoryFilter]);

    useEffect(() => {
        fetchTransactions();
    }, [fetchTransactions]);

    useEffect(() => {
        getCategoriesService().then(setCategories).catch(() => { });
    }, []);

    const handleSearch = (e) => {
        e.preventDefault();
        setSearch(searchInput);
        setPage(1);
    };

    const clearFilters = () => {
        setSearch('');
        setSearchInput('');
        setTypeFilter('');
        setCategoryFilter('');
        setPage(1);
    };

    const handleDelete = async (id) => {
        if (!confirm('¿Eliminar esta transacción?')) return;
        setDeletingId(id);
        try {
            await deleteTransactionService(id);
            toast.success('Transacción eliminada');
            fetchTransactions();
        } catch {
            toast.error('Error al eliminar');
        } finally {
            setDeletingId(null);
        }
    };

    const handleEdit = (transaction) => {
        setEditingTransaction(transaction);
        setShowModal(true);
    };

    const handleModalClose = () => {
        setShowModal(false);
        setEditingTransaction(null);
    };

    const handleModalSuccess = () => {
        handleModalClose();
        fetchTransactions();
    };

    const hasFilters = search || typeFilter || categoryFilter;

    return (
        <div className="space-y-6">
            {/* Header */}
            <div className="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
                <div>
                    <h1 className="text-2xl font-bold text-gray-900 sm:text-3xl">Transacciones</h1>
                    {pagination && (
                        <p className="text-sm text-gray-500 mt-0.5">
                            {pagination.total} registros en total
                        </p>
                    )}
                </div>
                <Button onClick={() => setShowModal(true)} className="w-full sm:w-auto">
                    <Plus size={16} />
                    Nueva transacción
                </Button>
            </div>

            {/* Filtros */}
            <Card className="p-4">
                <div className="flex flex-col gap-3 lg:flex-row lg:flex-wrap">
                    {/* Búsqueda */}
                    <form onSubmit={handleSearch} className="flex w-full gap-2 lg:flex-1 lg:min-w-48">
                        <div className="relative flex-1">
                            <Search size={15} className="absolute left-3 top-1/2
                -translate-y-1/2 text-gray-400" />
                            <input
                                value={searchInput}
                                onChange={(e) => setSearchInput(e.target.value)}
                                placeholder="Buscar por descripción..."
                                className="w-full rounded-xl border border-gray-200 py-2 pl-9 pr-4 text-sm focus:outline-none focus:ring-2 focus:ring-gray-900"
                            />
                        </div>
                        <Button type="submit" size="sm" variant="secondary">
                            <Filter size={14} />
                        </Button>
                    </form>

                    {/* Filtro por tipo */}
                    <select
                        value={typeFilter}
                        onChange={(e) => { setTypeFilter(e.target.value); setPage(1); }}
                        className="w-full rounded-xl border border-gray-200 bg-white px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-gray-900 lg:w-auto"
                    >
                        <option value="">Todos los tipos</option>
                        <option value="income">Ingresos</option>
                        <option value="expense">Gastos</option>
                    </select>

                    {/* Filtro por categoría */}
                    <select
                        value={categoryFilter}
                        onChange={(e) => { setCategoryFilter(e.target.value); setPage(1); }}
                        className="w-full rounded-xl border border-gray-200 bg-white px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-gray-900 lg:w-auto"
                    >
                        <option value="">Todas las categorías</option>
                        {categories.map((cat) => (
                            <option key={cat.id} value={cat.id}>
                                {cat.icon} {cat.name}
                            </option>
                        ))}
                    </select>

                    {/* Limpiar filtros */}
                    {hasFilters && (
                        <Button variant="ghost" size="sm" onClick={clearFilters} className="w-full sm:w-auto">
                            <X size={14} />
                            Limpiar
                        </Button>
                    )}
                </div>
            </Card>

            {/* Tabla */}
            {loading ? (
                <div className="flex justify-center py-20">
                    <Spinner size="lg" />
                </div>
            ) : transactions.length === 0 ? (
                <EmptyState
                    icon="💸"
                    title="Sin transacciones"
                    description={hasFilters
                        ? 'No hay resultados para los filtros aplicados'
                        : 'Añade tu primera transacción'
                    }
                    action={
                        !hasFilters && (
                            <Button onClick={() => setShowModal(true)}>
                                <Plus size={16} /> Añadir transacción
                            </Button>
                        )
                    }
                />
            ) : (
                <div className="space-y-3 lg:hidden">
                    {transactions.map((tx) => (
                        <Card key={tx.id} className="p-4">
                            <div className="flex items-start justify-between gap-4">
                                <div className="min-w-0 flex-1 space-y-3">
                                    <div>
                                        <p className="font-medium text-gray-900 break-words">
                                            {tx.description || '—'}
                                        </p>
                                        <p className="mt-1 text-xs text-gray-400">
                                            {new Date(tx.date).toLocaleDateString('es-ES', {
                                                day: '2-digit', month: 'short', year: 'numeric',
                                            })}
                                        </p>
                                    </div>

                                    <div className="flex flex-wrap items-center gap-2">
                                        <Badge variant={tx.type === 'income' ? 'income' : 'expense'}>
                                            {typeLabel[tx.type]}
                                        </Badge>
                                        {tx.category ? (
                                            <span className="inline-flex items-center gap-1.5 text-sm text-gray-600">
                                                <span
                                                    className="h-2.5 w-2.5 flex-shrink-0 rounded-full"
                                                    style={{ backgroundColor: tx.category.color }}
                                                />
                                                {tx.category.icon} {tx.category.name}
                                            </span>
                                        ) : (
                                            <span className="text-sm text-gray-400">Sin categoría</span>
                                        )}
                                    </div>
                                </div>

                                <div className="flex flex-col items-end gap-3">
                                    <span className={`font-semibold ${tx.type === 'income' ? 'text-emerald-600' : 'text-rose-600'}`}>
                                        {tx.type === 'income' ? '+' : '-'}
                                        ${Number(tx.amount).toLocaleString('es', {
                                            minimumFractionDigits: 2,
                                        })}
                                    </span>
                                    <div className="flex items-center gap-1">
                                        <button
                                            onClick={() => handleEdit(tx)}
                                            className="rounded-lg p-2 text-gray-400 transition-colors hover:bg-gray-100 hover:text-gray-700"
                                        >
                                            <Pencil size={14} />
                                        </button>
                                        <button
                                            onClick={() => handleDelete(tx.id)}
                                            disabled={deletingId === tx.id}
                                            className="rounded-lg p-2 text-gray-400 transition-colors hover:bg-rose-50 hover:text-rose-600 disabled:opacity-40"
                                        >
                                            <Trash2 size={14} />
                                        </button>
                                    </div>
                                </div>
                            </div>
                        </Card>
                    ))}
                </div>

                <Card className="hidden overflow-hidden lg:block">
                    <table className="w-full text-sm">
                        <thead className="bg-gray-50 border-b border-gray-100">
                            <tr>
                                <th className="text-left px-5 py-3.5 text-gray-500 font-medium">
                                    Descripción
                                </th>
                                <th className="text-left px-5 py-3.5 text-gray-500 font-medium">
                                    Categoría
                                </th>
                                <th className="text-left px-5 py-3.5 text-gray-500 font-medium">
                                    Fecha
                                </th>
                                <th className="text-left px-5 py-3.5 text-gray-500 font-medium">
                                    Tipo
                                </th>
                                <th className="text-right px-5 py-3.5 text-gray-500 font-medium">
                                    Monto
                                </th>
                                <th className="px-5 py-3.5" />
                            </tr>
                        </thead>
                        <tbody className="divide-y divide-gray-50">
                            {transactions.map((tx) => (
                                <tr key={tx.id} className="hover:bg-gray-50 transition-colors">
                                    <td className="px-5 py-3.5">
                                        <p className="font-medium text-gray-900 truncate max-w-48">
                                            {tx.description || '—'}
                                        </p>
                                    </td>
                                    <td className="px-5 py-3.5">
                                        {tx.category ? (
                                            <span className="flex items-center gap-1.5 text-sm text-gray-600">
                                                <span
                                                    className="w-2.5 h-2.5 rounded-full flex-shrink-0"
                                                    style={{ backgroundColor: tx.category.color }}
                                                />
                                                {tx.category.icon} {tx.category.name}
                                            </span>
                                        ) : (
                                            <span className="text-gray-400">Sin categoría</span>
                                        )}
                                    </td>
                                    <td className="px-5 py-3.5 text-gray-500">
                                        {new Date(tx.date).toLocaleDateString('es-ES', {
                                            day: '2-digit', month: 'short', year: 'numeric',
                                        })}
                                    </td>
                                    <td className="px-5 py-3.5">
                                        <Badge variant={tx.type === 'income' ? 'income' : 'expense'}>
                                            {typeLabel[tx.type]}
                                        </Badge>
                                    </td>
                                    <td className="px-5 py-3.5 text-right">
                                        <span className={`font-semibold ${tx.type === 'income' ? 'text-emerald-600' : 'text-rose-600'
                                            }`}>
                                            {tx.type === 'income' ? '+' : '-'}
                                            ${Number(tx.amount).toLocaleString('es', {
                                                minimumFractionDigits: 2,
                                            })}
                                        </span>
                                    </td>
                                    <td className="px-5 py-3.5">
                                        <div className="flex items-center justify-end gap-1">
                                            <button
                                                onClick={() => handleEdit(tx)}
                                                className="p-1.5 text-gray-400 hover:text-gray-700
                          hover:bg-gray-100 rounded-lg transition-colors"
                                            >
                                                <Pencil size={14} />
                                            </button>
                                            <button
                                                onClick={() => handleDelete(tx.id)}
                                                disabled={deletingId === tx.id}
                                                className="p-1.5 text-gray-400 hover:text-rose-600
                          hover:bg-rose-50 rounded-lg transition-colors
                          disabled:opacity-40"
                                            >
                                                <Trash2 size={14} />
                                            </button>
                                        </div>
                                    </td>
                                </tr>
                            ))}
                        </tbody>
                    </table>

                    {/* Paginación */}
                    {pagination && pagination.total_pages > 1 && (
                        <div className="flex flex-col gap-3 border-t border-gray-100 px-5 py-4 sm:flex-row sm:items-center sm:justify-between">
                            <p className="text-sm text-gray-500">
                                Página {pagination.page} de {pagination.total_pages}
                            </p>
                            <div className="flex flex-col gap-2 sm:flex-row">
                                <Button
                                    variant="secondary" size="sm"
                                    onClick={() => setPage((p) => p - 1)}
                                    disabled={page === 1}
                                >
                                    ← Anterior
                                </Button>
                                <Button
                                    variant="secondary" size="sm"
                                    onClick={() => setPage((p) => p + 1)}
                                    disabled={page === pagination.total_pages}
                                >
                                    Siguiente →
                                </Button>
                            </div>
                        </div>
                    )}
                </Card>
            )}

            {/* Modal */}
            {showModal && (
                <TransactionModal
                    transaction={editingTransaction}
                    categories={categories}
                    onClose={handleModalClose}
                    onSuccess={handleModalSuccess}
                />
            )}
        </div>
    );
};

export default TransactionsPage;