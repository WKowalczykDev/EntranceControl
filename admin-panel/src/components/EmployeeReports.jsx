import React, { useState, useEffect } from 'react';
import { UserCheck, ShieldAlert, BadgeAlert, Activity, BarChart3, Fingerprint, Clock, ScanLine } from 'lucide-react';
import { api } from '../services/api';

const EmployeeReports = ({ employees }) => {
    const [selectedDbId, setSelectedDbId] = useState('');
    const [stats, setStats] = useState(null);
    const [recentLogs, setRecentLogs] = useState([]);
    const [loading, setLoading] = useState(false);

    // Funkcja pomocnicza: Czy status oznacza sukces?
    const isSuccess = (status) => {
        const s = status ? status.toUpperCase() : "";
        return ["GRANTED", "MATCH", "SUKCES", "OK"].includes(s);
    };

    // Funkcja pomocnicza: Normalizacja procentów (naprawa błędu 4899%)
    const normalizeConfidence = (val) => {
        if (val === null || val === undefined) return 0;
        // Jeśli wartość > 1 (np. 97.9), to już jest procent -> zwróć bez zmian
        if (val > 1.0) return val;
        // Jeśli wartość <= 1 (np. 0.97), to ułamek -> pomnóż przez 100
        return val * 100;
    };

    useEffect(() => {
        const fetchLogs = async () => {
            if (!selectedDbId) {
                setStats(null);
                setRecentLogs([]);
                return;
            }
            setLoading(true);
            try {
                const logs = await api.getEmployeeLogs(selectedDbId);

                // 1. Liczenie statystyk z uwzględnieniem różnych nazw statusów
                const entries = logs.filter(l => isSuccess(l.status_finalny)).length;

                // Odmowy to wszystko co nie jest sukcesem
                const denied = logs.filter(l => !isSuccess(l.status_finalny)).length;

                const suspicious = logs.filter(l => l.podejrzana || (l.wynik_qr === 'OK' && l.wynik_biometryczny === 'NO_MATCH')).length;

                // 2. Obliczanie średniej zgodności (naprawa matematyki)
                // Najpierw normalizujemy każdą wartość do skali 0-100, potem sumujemy
                const totalConf = logs.reduce((acc, curr) => {
                    const val = curr.procent_podobienstwa || 0;
                    return acc + normalizeConfidence(val);
                }, 0);

                const avgConf = logs.length ? Math.round(totalConf / logs.length) : 0;

                setStats({ entries, denied, suspicious, efficiency: avgConf });
                setRecentLogs(logs);
            } catch (error) {
                console.error("Błąd pobierania raportu:", error);
            } finally {
                setLoading(false);
            }
        };
        fetchLogs();
    }, [selectedDbId]);

    const getStatusStyle = (status) => {
        if (isSuccess(status)) return 'bg-green-100 text-green-700 border-green-200';
        if (status?.includes('DENIED') || status === 'NO_MATCH' || status?.includes('ODMOWA')) return 'bg-red-100 text-red-700 border-red-200';
        return 'bg-gray-100 text-gray-700 border-gray-200';
    };

    const getStatusLabel = (status) => {
        if (isSuccess(status)) return "SUKCES";
        if (status?.includes('DENIED') || status === 'NO_MATCH') return "ODMOWA";
        return status || "-";
    };

    return (
        <div className="space-y-6 animate-in fade-in duration-500">
            <div className="bg-white p-6 rounded-2xl shadow-xl shadow-gray-200/50 border border-gray-100">
                <h2 className="text-lg font-bold text-gray-800 mb-4 flex items-center gap-2">
                    <BarChart3 className="text-indigo-600" size={20} /> Raport aktywności i Logi
                </h2>
                <div className="max-w-md">
                    <label className="block text-sm font-medium text-gray-700 mb-2">Wybierz pracownika</label>
                    <select value={selectedDbId} onChange={(e) => setSelectedDbId(e.target.value)} className="w-full px-4 py-2.5 bg-gray-50 border border-gray-200 rounded-xl outline-none focus:ring-2 focus:ring-indigo-500/20 cursor-pointer">
                        <option value="">-- Wybierz pracownika --</option>
                        {employees.map(emp => (
                            <option key={emp.id} value={emp.id}>{emp.firstName} {emp.lastName} (ID: {emp.employeeId})</option>
                        ))}
                    </select>
                </div>
            </div>

            {loading ? (
                <div className="text-center py-12 text-gray-500">Pobieranie logów...</div>
            ) : selectedDbId && stats ? (
                <>
                    <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
                        <div className="bg-white p-5 rounded-2xl shadow-sm border border-green-100 text-center"><span className="text-2xl font-bold">{stats.entries}</span><div className="text-xs text-gray-500 uppercase">Przyznane</div></div>
                        <div className="bg-white p-5 rounded-2xl shadow-sm border border-red-100 text-center"><span className="text-2xl font-bold">{stats.denied}</span><div className="text-xs text-gray-500 uppercase">Odmowy</div></div>
                        <div className="bg-white p-5 rounded-2xl shadow-sm border border-orange-100 text-center"><span className="text-2xl font-bold text-orange-600">{stats.suspicious}</span><div className="text-xs text-gray-500 uppercase">Incydenty</div></div>
                        <div className="bg-white p-5 rounded-2xl shadow-sm border border-indigo-100 text-center relative overflow-hidden"><span className="text-2xl font-bold relative z-10">{stats.efficiency}%</span><div className="text-xs text-gray-500 uppercase relative z-10">Zgodność twarzy</div><div className="absolute bottom-0 left-0 h-1.5 bg-indigo-500" style={{ width: `${Math.min(stats.efficiency, 100)}%` }}></div></div>
                    </div>

                    <div className="bg-white rounded-2xl shadow-sm border border-gray-100 overflow-hidden">
                        <table className="w-full text-sm text-left">
                            <thead className="text-xs text-gray-500 uppercase bg-gray-50 border-b border-gray-100">
                            <tr><th className="px-6 py-3">Czas</th><th className="px-6 py-3">Bramka</th><th className="px-6 py-3">QR</th><th className="px-6 py-3">Biometria</th><th className="px-6 py-3">Status</th></tr>
                            </thead>
                            <tbody className="divide-y divide-gray-100">
                            {recentLogs.map((log) => (
                                <tr key={log.id} className="hover:bg-gray-50">
                                    <td className="px-6 py-4 font-mono text-gray-600">{new Date(log.data_czas).toLocaleString()}</td>
                                    <td className="px-6 py-4">{log.bramka_id || '-'}</td>
                                    <td className="px-6 py-4">{log.wynik_qr}</td>

                                    {/* TUTAJ BYŁ BŁĄD PROCENTÓW - TERAZ JEST NAPRAWIONY */}
                                    <td className="px-6 py-4">
                                        {normalizeConfidence(log.procent_podobienstwa).toFixed(1)}%
                                    </td>

                                    <td className="px-6 py-4">
                                        <span className={`px-2 py-1 rounded text-xs font-bold ${getStatusStyle(log.status_finalny)}`}>
                                            {getStatusLabel(log.status_finalny)}
                                        </span>
                                    </td>
                                </tr>
                            ))}
                            </tbody>
                        </table>
                    </div>
                </>
            ) : null}
        </div>
    );
};

export default EmployeeReports;