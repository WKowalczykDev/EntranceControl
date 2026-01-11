import React from 'react';
import EmployeeRow from './EmployeeRow';
import { Users } from 'lucide-react';

const EmployeeTable = ({ employees, onEdit, onDelete }) => {
    return (
        <div className="bg-white rounded-2xl shadow-xl shadow-gray-200/50 border border-gray-100 overflow-hidden">
            <table className="w-full border-collapse">
                <thead className="bg-gray-50/50 border-b border-gray-100">
                <tr>
                    <th className="px-6 py-4 text-left text-xs font-semibold text-gray-500 uppercase tracking-wider">Pracownik</th>
                    <th className="px-6 py-4 text-left text-xs font-semibold text-gray-500 uppercase tracking-wider">ID</th>
                    <th className="px-6 py-4 text-left text-xs font-semibold text-gray-500 uppercase tracking-wider">Stanowisko</th>
                    <th className="px-6 py-4 text-right text-xs font-semibold text-gray-500 uppercase tracking-wider">Akcje</th>
                </tr>
                </thead>
                <tbody className="divide-y divide-gray-50">
                {employees.length === 0 ? (
                    <tr>
                        <td colSpan="4" className="px-6 py-12 text-center">
                            <div className="flex flex-col items-center justify-center text-gray-400">
                                <Users size={48} strokeWidth={1} className="mb-4 text-gray-300"/>
                                <p className="text-lg font-medium text-gray-500">Brak pracowników</p>
                                <p className="text-sm">Dodaj nową osobę, aby zobaczyć ją na liście.</p>
                            </div>
                        </td>
                    </tr>
                ) : (
                    employees.map(emp => (
                        <EmployeeRow
                            key={emp.id}
                            employee={emp}
                            onEdit={onEdit}
                            onDelete={onDelete}
                        />
                    ))
                )}
                </tbody>
            </table>
        </div>
    );
};

export default EmployeeTable;