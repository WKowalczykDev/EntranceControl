import React, { useState } from 'react';
import { Plus } from 'lucide-react';
import Header from './components/Header';
import EmployeeTable from './components/EmployeeTable';
import EmployeeModal from './components/EmployeeModal';

function App() {
    // Dane z dodanymi kolorami awatarów (symulacja)
    const [employees, setEmployees] = useState([
        { id: 'EMP001', firstName: 'Jan', lastName: 'Kowalski', position: 'Manager' },
        { id: 'EMP002', firstName: 'Anna', lastName: 'Nowak', position: 'Designer' },
        { id: 'EMP003', firstName: 'Piotr', lastName: 'Wiśniewski', position: 'Developer' },
    ]);

    const [showModal, setShowModal] = useState(false);
    const [editingEmployee, setEditingEmployee] = useState(null);

    const handleOpenModal = (employee = null) => {
        setEditingEmployee(employee);
        setShowModal(true);
    };

    const handleCloseModal = () => {
        setShowModal(false);
        setEditingEmployee(null);
    };

    const handleSaveEmployee = (formData) => {
        if (editingEmployee) {
            setEmployees(employees.map(emp =>
                emp.id === editingEmployee.id ? { ...emp, ...formData } : emp
            ));
        } else {
            const newEmployee = {
                ...formData,
                id: `EMP${String(employees.length + 1).padStart(3, '0')}`
            };
            setEmployees([...employees, newEmployee]);
        }
        handleCloseModal();
    };

    const handleDeleteEmployee = (id) => {
        if (confirm('Czy na pewno chcesz usunąć tego pracownika?')) {
            setEmployees(employees.filter(emp => emp.id !== id));
        }
    };

    return (
        // Zmiana: Tło bg-gray-50 z delikatnym gradientem
        <div className="min-h-screen bg-gray-50/50 text-gray-800 font-sans">
            <Header />

            <main className="max-w-6xl mx-auto p-6 lg:p-8">
                <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center mb-8 gap-4">
                    <div>
                        <h2 className="text-2xl font-bold text-gray-900 tracking-tight">Zespół</h2>
                        <p className="text-gray-500 mt-1">Zarządzaj listą pracowników i ich rolami.</p>
                    </div>

                    <button
                        onClick={() => handleOpenModal()}
                        className="group flex items-center gap-2 bg-indigo-600 hover:bg-indigo-700 text-white px-5 py-2.5 rounded-xl font-medium shadow-lg shadow-indigo-200 transition-all hover:scale-105 active:scale-95 cursor-pointer"
                    >
                        <Plus className="w-5 h-5 group-hover:rotate-90 transition-transform" />
                        Dodaj pracownika
                    </button>
                </div>

                <EmployeeTable
                    employees={employees}
                    onEdit={handleOpenModal}
                    onDelete={handleDeleteEmployee}
                />
            </main>

            <EmployeeModal
                isOpen={showModal}
                onClose={handleCloseModal}
                onSave={handleSaveEmployee}
                employee={editingEmployee}
            />
        </div>
    );
}

export default App;