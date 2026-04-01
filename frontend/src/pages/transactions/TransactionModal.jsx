import { useState, useEffect } from 'react';
import { X } from 'lucide-react';
import {
    createTransactionService,
    updateTransactionService,
} from '../../services/transaction.service.js';
import Button from '../../components/ui/Button.jsx';
import toast from 'react-hot-toast';

const TransactionModal = ({ transaction, categories, onClose, onSuccess }) => {
    const isEditing = !!transaction;

    const [form, setForm] = useState({
        amount: '',
        description: '',
        type: 'expense',
        date: new Date().toISOString().split('T')[0],
        category_id: '',
    });
    const [loading, setLoading] = useState(false);

    // Si estamos editando, precargamos los datos
    useEffect(() => {
        if (transaction) {
            setForm({
                amount: String(transaction.amount),
                description: transaction.description || '',
                type: transaction.type,
                date: transaction.date?.split('T')[0] || '',
                category_id: transaction.category?.id || '',
            });
        }
    }, [transaction]);

    const handleSubmit = async (e) => {
        e.preventDefault();
        setLoading(true);
        try {
            const payload = {
                ...form,
                amount: parseFloat(form.amount),
                category_id: form.category_id ? parseInt(form.category_id) : null,
                date: `${form.date}T12:00:00Z`,
            };

            if (isEditing) {
                await updateTransactionService(transaction.id, payload);
                toast.success('Transacción actualizada');
            } else {
                await createTransactionService(payload);
                toast.success('Transacción creada');
            }
            onSuccess();
        } catch (error) {
            toast.error(error.response?.data?.detail || 'Error al guardar');
        } finally {
            setLoading(false);
        }
    };

    return (
        // Overlay oscuro detrás del modal
        <div className="fixed inset-0 bg-black/40 z-50 flex items-center
      justify-center p-4" onClick={onClose}>
            <div
                className="bg-white rounded-2xl w-full max-w-md shadow-xl"
                onClick={(e) => e.stopPropagation()} // Evita cerrar al hacer clic dentro
            >
                {/* Header */}
                <div className="flex items-center justify-between px-6 py-5
          border-b border-gray-100">
                    <h2 className="font-semibold text-gray-900">
                        {isEditing ? 'Editar transacción' : 'Nueva transacción'}
                    </h2>
                    <button
                        onClick={onClose}
                        className="p-1.5 text-gray-400 hover:text-gray-700
              hover:bg-gray-100 rounded-lg transition-colors"
                    >
                        <X size={18} />
                    </button>
                </div>

                <form onSubmit={handleSubmit} className="p-6 space-y-4">
                    {/* Tipo */}
                    <div className="grid grid-cols-2 gap-2 p-1 bg-gray-100 rounded-xl">
                        {['expense', 'income'].map((type) => (
                            <button
                                key={type}
                                type="button"
                                onClick={() => setForm({ ...form, type })}
                                className={`py-2 rounded-lg text-sm font-medium transition-colors ${form.type === type
                                        ? type === 'expense'
                                            ? 'bg-white text-rose-600 shadow-sm'
                                            : 'bg-white text-emerald-600 shadow-sm'
                                        : 'text-gray-500 hover:text-gray-700'
                                    }`}
                            >
                                {type === 'expense' ? '💸 Gasto' : '💰 Ingreso'}
                            </button>
                        ))}
                    </div>

                    {/* Monto */}
                    <div>
                        <label className="block text-sm font-medium text-gray-700 mb-1.5">
                            Monto
                        </label>
                        <div className="relative">
                            <span className="absolute left-3.5 top-1/2 -translate-y-1/2
                text-gray-400 font-medium">$</span>
                            <input
                                type="number"
                                step="0.01"
                                min="0.01"
                                value={form.amount}
                                onChange={(e) => setForm({ ...form, amount: e.target.value })}
                                required
                                placeholder="0.00"
                                className="w-full pl-8 pr-4 py-2.5 border border-gray-200
                  rounded-xl text-sm focus:outline-none focus:ring-2
                  focus:ring-gray-900"
                            />
                        </div>
                    </div>

                    {/* Descripción */}
                    <div>
                        <label className="block text-sm font-medium text-gray-700 mb-1.5">
                            Descripción
                        </label>
                        <input
                            type="text"
                            value={form.description}
                            onChange={(e) => setForm({ ...form, description: e.target.value })}
                            placeholder="Ej: Supermercado, Salario..."
                            className="w-full px-4 py-2.5 border border-gray-200 rounded-xl
                text-sm focus:outline-none focus:ring-2 focus:ring-gray-900"
                        />
                    </div>

                    {/* Fecha */}
                    <div>
                        <label className="block text-sm font-medium text-gray-700 mb-1.5">
                            Fecha
                        </label>
                        <input
                            type="date"
                            value={form.date}
                            onChange={(e) => setForm({ ...form, date: e.target.value })}
                            required
                            className="w-full px-4 py-2.5 border border-gray-200 rounded-xl
                text-sm focus:outline-none focus:ring-2 focus:ring-gray-900"
                        />
                    </div>

                    {/* Categoría */}
                    <div>
                        <label className="block text-sm font-medium text-gray-700 mb-1.5">
                            Categoría
                        </label>
                        <select
                            value={form.category_id}
                            onChange={(e) => setForm({ ...form, category_id: e.target.value })}
                            className="w-full px-4 py-2.5 border border-gray-200 rounded-xl
                text-sm focus:outline-none focus:ring-2 focus:ring-gray-900
                bg-white"
                        >
                            <option value="">Sin categoría</option>
                            {categories.map((cat) => (
                                <option key={cat.id} value={cat.id}>
                                    {cat.icon} {cat.name}
                                </option>
                            ))}
                        </select>
                    </div>

                    {/* Botones */}
                    <div className="flex gap-3 pt-2">
                        <Button type="submit" loading={loading} className="flex-1">
                            {isEditing ? 'Guardar cambios' : 'Crear transacción'}
                        </Button>
                        <Button type="button" variant="secondary" onClick={onClose}>
                            Cancelar
                        </Button>
                    </div>
                </form>
            </div>
        </div>
    );
};

export default TransactionModal;