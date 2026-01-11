import React from 'react';
import { Pencil, Trash2 } from 'lucide-react';

const EmployeeRow = ({ employee, onEdit, onDelete }) => {
    // Generowanie inicjałów
    const initials = `${employee.firstName[0]}${employee.lastName[0]}`;

    // Prosta funkcja do kolorów badge w zależności od stanowiska (opcjonalne)
    const getRoleColor = (role) => {
        const r = role.toLowerCase();
        if (r.includes('manager') || r.includes('kierownik')) return 'bg-purple-100 text-purple-700 border-purple-200';
        if (r.includes('dev') || r.includes('programista')) return 'bg-blue-100 text-blue-700 border-blue-200';
        if (r.includes('design') || r.includes('grafik')) return 'bg-pink-100 text-pink-700 border-pink-200';
        return 'bg-gray-100 text-gray-700 border-gray-200';
    };

    return (
        <tr className="group hover:bg-gray-50/80 transition-colors duration-200">
            <td className="px-6 py-4 whitespace-nowrap">
                <div className="flex items-center gap-4">
                    <div className="w-10 h-10 rounded-full bg-gradient-to-br from-indigo-500 to-purple-600 text-white flex items-center justify-center text-sm font-bold shadow-sm ring-2 ring-white">
                        {initials}
                    </div>
                    <div>
                        <div className="text-sm font-semibold text-gray-900">
                            {employee.firstName} {employee.lastName}
                        </div>
                        <div className="text-xs text-gray-500">user@example.com</div>
                    </div>
                </div>
            </td>

            <td className="px-6 py-4 whitespace-nowrap">
                <span className="text-xs font-mono text-gray-400 bg-gray-50 px-2 py-1 rounded border border-gray-100">
                    {employee.id}
                </span>
            </td>

            <td className="px-6 py-4 whitespace-nowrap">
                <span className={`px-3 py-1 inline-flex text-xs leading-5 font-medium rounded-full border ${getRoleColor(employee.position)}`}>
                    {employee.position}
                </span>
            </td>

            <td className="px-6 py-4 whitespace-nowrap text-right text-sm font-medium">
                <div className="flex items-center justify-end gap-2 opacity-0 group-hover:opacity-100 transition-opacity duration-200">
                    <button
                        onClick={() => onEdit(employee)}
                        className="p-2 text-indigo-600 hover:bg-indigo-50 rounded-lg transition-colors cursor-pointer"
                        title="Edytuj"
                    >
                        <Pencil size={16} />
                    </button>
                    <button
                        onClick={() => onDelete(employee.id)}
                        className="p-2 text-red-500 hover:bg-red-50 rounded-lg transition-colors cursor-pointer"
                        title="Usuń"
                    >
                        <Trash2 size={16} />
                    </button>
                </div>
            </td>
        </tr>
    );
};

export default EmployeeRow;