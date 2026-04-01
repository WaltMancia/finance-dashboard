import { useState, useRef } from 'react';
import { Upload, FileText, CheckCircle, XCircle, AlertCircle } from 'lucide-react';
import { previewCSVService, importCSVService } from '../../services/csv.service.js';
import Button from '../../components/ui/Button.jsx';
import Card, { CardHeader, CardContent } from '../../components/ui/Card.jsx';
import Badge from '../../components/ui/Badge.jsx';
import Spinner from '../../components/ui/Spinner.jsx';
import toast from 'react-hot-toast';

// Los 3 pasos del proceso de importación
const STEPS = { SELECT: 1, PREVIEW: 2, DONE: 3 };

const ImportPage = () => {
    const [step, setStep] = useState(STEPS.SELECT);
    const [file, setFile] = useState(null);
    const [preview, setPreview] = useState(null);
    const [selectedCategory, setSelectedCategory] = useState('');
    const [loading, setLoading] = useState(false);
    const [result, setResult] = useState(null);
    const fileInputRef = useRef(null);

    const handleFileSelect = (e) => {
        const selected = e.target.files?.[0];
        if (!selected) return;
        if (!selected.name.toLowerCase().endsWith('.csv')) {
            toast.error('Solo se permiten archivos .csv');
            return;
        }
        setFile(selected);
        setPreview(null);
        setResult(null);
        setStep(STEPS.SELECT);
    };

    const handlePreview = async () => {
        if (!file) return;
        setLoading(true);
        try {
            const data = await previewCSVService(file);
            setPreview(data);
            setStep(STEPS.PREVIEW);
        } catch (error) {
            toast.error(error.response?.data?.detail || 'Error al leer el CSV');
        } finally {
            setLoading(false);
        }
    };

    const handleImport = async () => {
        if (!file) return;
        setLoading(true);
        try {
            const data = await importCSVService(
                file,
                selectedCategory ? parseInt(selectedCategory) : null
            );
            setResult(data);
            setStep(STEPS.DONE);
            toast.success(`¡${data.rows_imported} transacciones importadas!`);
        } catch (error) {
            toast.error(error.response?.data?.detail || 'Error al importar');
        } finally {
            setLoading(false);
        }
    };

    const handleReset = () => {
        setStep(STEPS.SELECT);
        setFile(null);
        setPreview(null);
        setResult(null);
        setSelectedCategory('');
        if (fileInputRef.current) fileInputRef.current.value = '';
    };

    return (
        <div className="max-w-2xl mx-auto space-y-6">
            <div>
                <h1 className="text-2xl font-bold text-gray-900">Importar CSV</h1>
                <p className="text-gray-500 text-sm mt-0.5">
                    Importa transacciones desde el extracto de tu banco
                </p>
            </div>

            {/* Indicador de pasos */}
            <div className="flex items-center gap-2">
                {[
                    { n: 1, label: 'Seleccionar archivo' },
                    { n: 2, label: 'Previsualizar' },
                    { n: 3, label: 'Completado' },
                ].map(({ n, label }, i) => (
                    <div key={n} className="flex items-center gap-2 flex-1">
                        <div className={`w-7 h-7 rounded-full flex items-center justify-center
              text-xs font-bold shrink-0 ${step >= n
                                ? 'bg-gray-900 text-white'
                                : 'bg-gray-100 text-gray-400'
                            }`}>
                            {step > n ? '✓' : n}
                        </div>
                        <span className={`text-xs ${step >= n ? 'text-gray-900' : 'text-gray-400'}`}>
                            {label}
                        </span>
                        {i < 2 && <div className="flex-1 h-px bg-gray-200 ml-2" />}
                    </div>
                ))}
            </div>

            {/* PASO 1 — Seleccionar archivo */}
            {step === STEPS.SELECT && (
                <Card>
                    <CardContent className="pt-6">
                        {/* Zona de drop */}
                        <div
                            onClick={() => fileInputRef.current?.click()}
                            className={`border-2 border-dashed rounded-2xl p-10 text-center
                cursor-pointer transition-colors ${file
                                    ? 'border-emerald-300 bg-emerald-50'
                                    : 'border-gray-200 hover:border-gray-300 hover:bg-gray-50'
                                }`}
                        >
                            {file ? (
                                <>
                                    <CheckCircle size={36} className="text-emerald-500 mx-auto mb-3" />
                                    <p className="font-medium text-gray-900">{file.name}</p>
                                    <p className="text-sm text-gray-500 mt-1">
                                        {(file.size / 1024).toFixed(1)} KB — Haz clic para cambiar
                                    </p>
                                </>
                            ) : (
                                <>
                                    <Upload size={36} className="text-gray-300 mx-auto mb-3" />
                                    <p className="font-medium text-gray-700">
                                        Haz clic para seleccionar un CSV
                                    </p>
                                    <p className="text-sm text-gray-400 mt-1">
                                        Máximo 5MB · Solo archivos .csv
                                    </p>
                                </>
                            )}
                        </div>

                        <input
                            ref={fileInputRef}
                            type="file"
                            accept=".csv"
                            onChange={handleFileSelect}
                            className="hidden"
                        />

                        {/* Mensaje de categoría detectada automáticamente */}
                        {file && (
                            <div className="mt-4 flex items-start gap-2.5 p-3.5 bg-emerald-50
    border border-emerald-100 rounded-xl">
                                <span className="text-emerald-500 mt-0.5 shrink-0">✨</span>
                                <div>
                                    <p className="text-sm font-medium text-emerald-800">
                                        Detección automática de categorías
                                    </p>
                                    <p className="text-xs text-emerald-600 mt-0.5 leading-relaxed">
                                        El sistema detectará la categoría de cada transacción
                                        automáticamente según su descripción.
                                    </p>
                                </div>
                            </div>
                        )}

                        <Button
                            className="w-full mt-4"
                            onClick={handlePreview}
                            disabled={!file}
                            loading={loading}
                        >
                            <FileText size={16} />
                            Previsualizar archivo
                        </Button>

                        {/* Formatos aceptados */}
                        <div className="mt-5 p-4 bg-blue-50 rounded-xl">
                            <p className="text-xs font-semibold text-blue-800 mb-2 flex items-center gap-1">
                                <AlertCircle size={13} />
                                Formatos aceptados
                            </p>
                            <p className="text-xs text-blue-700 leading-relaxed">
                                El CSV debe tener columnas de <strong>fecha</strong>, <strong>descripción</strong>,{' '}
                                <strong>monto</strong> y <strong>tipo</strong> (o columnas separadas de débito/crédito).
                                Se detectan automáticamente separadores de coma, punto y coma o tabulador, y la categoría
                                por fila según la descripción o la columna de categoría si existe.
                            </p>
                        </div>
                    </CardContent>
                </Card>
            )}

            {/* PASO 2 — Preview */}
            {step === STEPS.PREVIEW && preview && (
                <div className="space-y-4">
                    {/* Resumen del análisis */}
                    <div className="grid grid-cols-3 gap-3">
                        {[
                            { label: 'Total filas', value: preview.total_rows, color: 'text-gray-900' },
                            { label: 'Válidas', value: preview.valid_rows, color: 'text-emerald-600' },
                            { label: 'Inválidas', value: preview.invalid_rows, color: 'text-rose-600' },
                        ].map(({ label, value, color }) => (
                            <Card key={label} className="text-center p-4">
                                <p className={`text-2xl font-bold ${color}`}>{value}</p>
                                <p className="text-xs text-gray-500 mt-0.5">{label}</p>
                            </Card>
                        ))}
                    </div>

                    {/* Tabla de preview */}
                    <Card className="overflow-hidden">
                        <CardHeader>
                            <h3 className="font-semibold text-gray-900">
                                Vista previa (primeras {preview.preview.length} filas)
                            </h3>
                        </CardHeader>
                        <div className="max-h-96 overflow-auto">
                            <table className="w-full text-sm">
                                <thead className="sticky top-0 z-10 bg-gray-50 border-y border-gray-100">
                                    <tr>
                                        <th className="text-left px-4 py-3 text-gray-500 font-medium">#</th>
                                        <th className="text-left px-4 py-3 text-gray-500 font-medium">Fecha</th>
                                        <th className="text-left px-4 py-3 text-gray-500 font-medium">Descripción</th>
                                        <th className="text-left px-4 py-3 text-gray-500 font-medium">Monto</th>
                                        <th className="text-left px-4 py-3 text-gray-500 font-medium">Tipo</th>
                                        <th className="text-left px-4 py-3 text-gray-500 font-medium">Categoría</th>
                                        <th className="text-left px-4 py-3 text-gray-500 font-medium">Estado</th>
                                    </tr>
                                </thead>
                                <tbody className="divide-y divide-gray-50">
                                    {preview.preview.map((row) => (
                                        <tr key={row.row_number}
                                            className={row.is_valid ? '' : 'bg-rose-50'}>
                                            <td className="px-4 py-3 text-gray-400">{row.row_number}</td>
                                            <td className="px-4 py-3 text-gray-700">{row.date}</td>
                                            <td className="px-4 py-3 text-gray-700 max-w-36 truncate">
                                                {row.description || '—'}
                                            </td>
                                            <td className="px-4 py-3 font-medium">
                                                ${row.amount?.toFixed(2)}
                                            </td>
                                            <td className="px-4 py-3">
                                                <Badge variant={row.type === 'income' ? 'income' : 'expense'}>
                                                    {row.type === 'income' ? 'Ingreso' : 'Gasto'}
                                                </Badge>
                                            </td>
                                            <td className="px-4 py-3">
                                                <Badge variant="info">
                                                    {row.category_name || 'Otros'}
                                                </Badge>
                                            </td>
                                            <td className="px-4 py-3">
                                                {row.is_valid ? (
                                                    <CheckCircle size={16} className="text-emerald-500" />
                                                ) : (
                                                    <div className="flex items-center gap-1">
                                                        <XCircle size={16} className="text-rose-500 shrink-0" />
                                                        <span className="text-xs text-rose-600">{row.error}</span>
                                                    </div>
                                                )}
                                            </td>
                                        </tr>
                                    ))}
                                </tbody>
                            </table>
                        </div>
                    </Card>

                    <div className="flex gap-3">
                        <Button
                            className="flex-1"
                            onClick={handleImport}
                            loading={loading}
                            disabled={preview.valid_rows === 0}
                        >
                            Importar {preview.valid_rows} transacciones válidas
                        </Button>
                        <Button variant="secondary" onClick={handleReset}>
                            Cancelar
                        </Button>
                    </div>
                </div>
            )}

            {/* PASO 3 — Resultado */}
            {step === STEPS.DONE && result && (
                <Card>
                    <CardContent className="pt-8 pb-8 text-center">
                        <CheckCircle size={48} className="text-emerald-500 mx-auto mb-4" />
                        <h3 className="text-xl font-bold text-gray-900 mb-2">
                            ¡Importación completada!
                        </h3>
                        <p className="text-gray-500 mb-6">
                            Se importaron {result.rows_imported} transacciones exitosamente.
                            {result.rows_skipped > 0 && (
                                <span className="block text-sm mt-1">
                                    {result.rows_skipped} filas fueron omitidas por errores.
                                </span>
                            )}
                        </p>
                        <div className="flex gap-3 justify-center">
                            <Button onClick={handleReset}>
                                Importar otro archivo
                            </Button>
                            <Button variant="secondary" onClick={() => window.location.href = '/'}>
                                Ver dashboard
                            </Button>
                        </div>
                    </CardContent>
                </Card>
            )}
        </div>
    );
};

export default ImportPage;