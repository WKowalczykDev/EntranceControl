import React, { useState, useEffect } from 'react';
import { UserCheck, ShieldAlert, BadgeAlert, Activity, BarChart3, Fingerprint, Clock, ScanLine } from 'lucide-react';
import { api } from '../services/api';

const EmployeeReports = ({ employees }) => {
    const [selectedDbId, setSelectedDbId] = useState('');
    const [stats, setStats] = useState(null);
    const [recentLogs, setRecentLogs] = useState([]);
    const [loading, setLoading] = useState(false);

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

                const entries = logs.filter(l => l.status_finalny === 'GRANTED').length;
                const denied = logs.filter(l => l.status_finalny !== 'GRANTED').length;
                const suspicious = logs.filter(l => l.podejrzana || (l.wynik_qr === 'OK' && l.wynik_biometryczny === 'NO_MATCH')).length;

                const totalConf = logs.reduce((acc, curr) => acc + (curr.procent_podobienstwa || 0), 0);
                const avgConf = logs.length ? Math.round((totalConf / logs.length) * 100) : 0;

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
        if (status === 'GRANTED') return 'bg-green-100 text-green-700 border-green-200';
        if (status === 'DENIED') return 'bg-red-100 text-red-700 border-red-200';
        return 'bg-gray-100 text-gray-700 border-gray-200';
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
                        <div className="bg-white p-5 rounded-2xl shadow-sm border border-indigo-100 text-center relative overflow-hidden"><span className="text-2xl font-bold relative z-10">{stats.efficiency}%</span><div className="text-xs text-gray-500 uppercase relative z-10">Zgodność twarzy</div><div className="absolute bottom-0 left-0 h-1.5 bg-indigo-500" style={{ width: `${stats.efficiency}%` }}></div></div>
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
                                    <td className="px-6 py-4">{(log.procent_podobienstwa * 100).toFixed(1)}%</td>
                                    <td className="px-6 py-4"><span className={`px-2 py-1 rounded text-xs font-bold ${getStatusStyle(log.status_finalny)}`}>{log.status_finalny}</span></td>
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