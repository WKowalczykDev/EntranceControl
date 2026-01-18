import React from 'react';
import { Pencil, Trash2, CalendarCheck, QrCode } from 'lucide-react';

const EmployeeRow = ({ employee, onEdit, onDelete, onGenerateQr }) => {
    const initials = `${employee.firstName[0]}${employee.lastName[0]}`;

    return (
        <tr className={`group transition-colors duration-200 ${!employee.isActive ? 'bg-gray-50 opacity-70' : 'hover:bg-gray-50/80'}`}>
            <td className="px-6 py-4 whitespace-nowrap">
                <div className="flex items-center gap-4">
                    <div className={`w-10 h-10 rounded-full flex items-center justify-center text-sm font-bold shadow-sm text-white ${employee.isActive ? 'bg-gradient-to-br from-indigo-500 to-purple-600' : 'bg-gray-400'}`}>
                        {initials}
                    </div>
                    <div>
                        <div className="text-sm font-semibold text-gray-900">{employee.firstName} {employee.lastName}</div>
                        <div className="text-xs text-gray-500 font-mono">{employee.employeeId}</div>
                    </div>
                </div>
            </td>

            <td className="px-6 py-4 whitespace-nowrap">
                <div className="text-sm text-gray-600">{employee.email}</div>
                <div className="text-xs text-gray-400 flex items-center gap-1 mt-0.5">
                    <CalendarCheck size={10} /> {employee.hireDate}
                </div>
            </td>

            <td className="px-6 py-4 whitespace-nowrap">
                <span className="text-sm text-gray-700 bg-gray-100 px-2 py-1 rounded-md border border-gray-200">{employee.position}</span>
            </td>

            <td className="px-6 py-4 whitespace-nowrap">
                <span className={`px-2 py-1 inline-flex text-xs leading-5 font-semibold rounded-full border ${employee.isActive ? 'bg-green-100 text-green-700 border-green-200' : 'bg-red-50 text-red-600 border-red-100'}`}>
                    {employee.isActive ? 'Aktywny' : 'Zablokowany'}
                </span>
            </td>

            <td className="px-6 py-4 whitespace-nowrap text-right text-sm font-medium">
                <div className="flex items-center justify-end gap-2 opacity-0 group-hover:opacity-100 transition-opacity">
                    {/* Przycisk QR */}
                    <button onClick={() => onGenerateQr(employee)} className="p-2 text-gray-600 hover:text-gray-900 hover:bg-gray-100 rounded-lg cursor-pointer" title="Generuj QR">
                        <QrCode size={18} />
                    </button>
                    <button onClick={() => onEdit(employee)} className="p-2 text-indigo-600 hover:bg-indigo-50 rounded-lg cursor-pointer">
                        <Pencil size={16} />
                    </button>
                    <button onClick={() => onDelete(employee.id)} className="p-2 text-red-500 hover:bg-red-50 rounded-lg cursor-pointer">
                        <Trash2 size={16} />
                    </button>
                </div>
            </td>
        </tr>
    );
};

export default EmployeeRow;