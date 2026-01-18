import React, { useState, useEffect } from 'react';
import { Plus, Users, FileBarChart, RefreshCw } from 'lucide-react';
import Header from './components/Header';
import EmployeeTable from './components/EmployeeTable';
import EmployeeModal from './components/EmployeeModal';
import EmployeeReports from './components/EmployeeReports';
import QrCodeModal from './components/QrCodeModal';
import { api } from './services/api';

function App() {
    const [currentView, setCurrentView] = useState('employees');
    const [employees, setEmployees] = useState([]);
    const [loading, setLoading] = useState(false);

    // Stan Modala Pracownika
    const [showModal, setShowModal] = useState(false);
    const [editingEmployee, setEditingEmployee] = useState(null);

    // Stan Modala QR
    const [showQrModal, setShowQrModal] = useState(false);
    const [qrUrl, setQrUrl] = useState(null);
    const [qrEmployeeName, setQrEmployeeName] = useState('');

    useEffect(() => { loadEmployees(); }, []);

    const loadEmployees = async () => {
        setLoading(true);
        try {
            const data = await api.getEmployees();
            setEmployees(data);
        } catch (error) {
            console.error(error);
        } finally {
            setLoading(false);
        }
    };

    const handleOpenModal = (employee = null) => {
        setEditingEmployee(employee);
        setShowModal(true);
    };

    const handleCloseModal = () => {
        setShowModal(false);
        setEditingEmployee(null);
    };

    const handleSaveEmployee = async (formData) => {
        try {
            let savedDbId = null;
            if (editingEmployee) {
                savedDbId = editingEmployee.id;
                // Opcjonalnie: update danych tekstowych
            } else {
                const nextIdString = `EMP${String(employees.length + 1).padStart(3, '0')}`;
                const response = await api.createEmployee({ ...formData, id: nextIdString });
                savedDbId = response.id;
            }

            // Masowe wgrywanie zdjęć
            if (formData.photoFiles && formData.photoFiles.length > 0 && savedDbId) {
                const uploadPromises = formData.photoFiles.map(file => api.uploadPhoto(savedDbId, file));
                await Promise.all(uploadPromises);
            }

            await loadEmployees();
            handleCloseModal();
        } catch (error) {
            alert("Błąd: " + error.message);
        }
    };

    const handleDeleteEmployee = async (id) => {
        if (confirm('Usunąć pracownika?')) {
            try {
                await api.deleteEmployee(id);
                await loadEmployees();
            } catch (error) {
                alert(error.message);
            }
        }
    };

    // Obsługa QR
    const handleGenerateQr = async (employee) => {
        try {
            const url = await api.generateQrPass(employee.id);
            setQrUrl(url);
            setQrEmployeeName(`${employee.firstName} ${employee.lastName}`);
            setShowQrModal(true);
        } catch (error) {
            alert(error.message);
        }
    };

    const handleCloseQrModal = () => {
        setShowQrModal(false);
        setQrUrl(null);
    };

    return (
        <div className="min-h-screen bg-gray-50/50 text-gray-800 font-sans">
            <Header />

            <main className="max-w-7xl mx-auto p-6 lg:p-8">
                <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center mb-8 gap-4">
                    <div>
                        <h2 className="text-2xl font-bold text-gray-900 tracking-tight">Panel Administratora</h2>
                        <p className="text-gray-500 mt-1">System kontroli dostępu i zarządzania personelem.</p>
                    </div>
                    {currentView === 'employees' && (
                        <button onClick={() => handleOpenModal()} className="group flex items-center gap-2 bg-indigo-600 hover:bg-indigo-700 text-white px-5 py-2.5 rounded-xl font-medium shadow-lg shadow-indigo-200 transition-all hover:scale-105 active:scale-95 cursor-pointer">
                            <Plus className="w-5 h-5 group-hover:rotate-90 transition-transform" /> Dodaj pracownika
                        </button>
                    )}
                </div>

                <div className="flex items-center justify-between mb-6">
                    <div className="flex space-x-1 bg-gray-100/50 p-1 rounded-xl border border-gray-200">
                        <button onClick={() => setCurrentView('employees')} className={`flex items-center gap-2 px-4 py-2 rounded-lg text-sm font-medium transition-all cursor-pointer ${currentView === 'employees' ? 'bg-white text-indigo-600 shadow-sm' : 'text-gray-500'}`}>
                            <Users size={16} /> Pracownicy
                        </button>
                        <button onClick={() => setCurrentView('reports')} className={`flex items-center gap-2 px-4 py-2 rounded-lg text-sm font-medium transition-all cursor-pointer ${currentView === 'reports' ? 'bg-white text-indigo-600 shadow-sm' : 'text-gray-500'}`}>
                            <FileBarChart size={16} /> Raporty
                        </button>
                    </div>
                    <button onClick={loadEmployees} className="p-2 text-gray-400 hover:text-indigo-600 cursor-pointer"><RefreshCw size={18} className={loading ? "animate-spin" : ""} /></button>
                </div>

                <div className="transition-all duration-300 min-h-[400px]">
                    {loading && employees.length === 0 ? (
                        <div className="text-center py-12 text-gray-400">Ładowanie...</div>
                    ) : (
                        currentView === 'employees' ? (
                            <EmployeeTable employees={employees} onEdit={handleOpenModal} onDelete={handleDeleteEmployee} onGenerateQr={handleGenerateQr} />
                        ) : (
                            <EmployeeReports employees={employees} />
                        )
                    )}
                </div>
            </main>

            <EmployeeModal isOpen={showModal} onClose={handleCloseModal} onSave={handleSaveEmployee} employee={editingEmployee} />
            <QrCodeModal isOpen={showQrModal} onClose={handleCloseQrModal} qrUrl={qrUrl} employeeName={qrEmployeeName} />
        </div>
    );
}

export default App;