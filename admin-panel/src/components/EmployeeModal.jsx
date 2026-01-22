import React, { useState, useEffect, useRef } from 'react';
import { X, Calendar, Mail, UploadCloud, Trash2, RefreshCw } from 'lucide-react';

const EmployeeModal = ({ isOpen, onClose, onSave, employee }) => {
    const fileInputRef = useRef(null);
    const formRef = useRef(null); // Referencja do formularza
    const [isSubmitting, setIsSubmitting] = useState(false);

    const [formData, setFormData] = useState({
        firstName: '',
        lastName: '',
        email: '',
        position: '',
        hireDate: '',
        isActive: true,
        photoFiles: [],
        photoPreviews: []
    });

    useEffect(() => {
        setIsSubmitting(false); // Reset przy otwarciu
        if (employee) {
            setFormData({
                firstName: employee.firstName,
                lastName: employee.lastName,
                email: employee.email || '',
                position: employee.position,
                hireDate: employee.hireDate || '',
                isActive: employee.isActive ?? true,
                photoFiles: [],
                photoPreviews: []
            });
        } else {
            setFormData({
                firstName: '', lastName: '', email: '', position: '', hireDate: '', isActive: true,
                photoFiles: [], photoPreviews: []
            });
        }
    }, [employee, isOpen]);

    const handleFileChange = (e) => {
        if (e.target.files && e.target.files.length > 0) {
            const newFiles = Array.from(e.target.files);
            const newPreviews = newFiles.map(file => URL.createObjectURL(file));

            setFormData(prev => ({
                ...prev,
                photoFiles: [...prev.photoFiles, ...newFiles],
                photoPreviews: [...prev.photoPreviews, ...newPreviews]
            }));
        }
    };

    const handleRemovePhoto = (index) => {
        setFormData(prev => {
            const newFiles = [...prev.photoFiles];
            const newPreviews = [...prev.photoPreviews];
            newFiles.splice(index, 1);
            newPreviews.splice(index, 1);
            return { ...prev, photoFiles: newFiles, photoPreviews: newPreviews };
        });
        if (fileInputRef.current) fileInputRef.current.value = "";
    };

    // Zmieniona funkcja obsługi zapisu
    const handleManualSubmit = async (e) => {
        e.preventDefault(); // Zatrzymaj domyślne odświeżanie

        // 1. Sprawdź czy pola są wypełnione (Ręczna walidacja)
        if (!formData.firstName || !formData.lastName || !formData.email || !formData.hireDate) {
            alert("⚠️ Uzupełnij wymagane pola: Imię, Nazwisko, Email i Data zatrudnienia!");
            return;
        }

        // 2. Włączamy kółeczko
        setIsSubmitting(true);
        console.log("Rozpoczynam wysyłanie...");

        try {
            // Czekamy na wykonanie onSave z App.jsx
            await onSave(formData);

            // Jeśli się uda, modal się zamknie dzięki onClose w rodzicu
            // Ale dla pewności resetujemy stan
            setIsSubmitting(false);
        } catch (error) {
            console.error("Błąd zapisu:", error);
            alert("Wystąpił błąd podczas zapisu: " + error.message);
            setIsSubmitting(false); // Wyłączamy kółeczko, żeby można było spróbować ponownie
        }
    };

    if (!isOpen) return null;

    return (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4">
            {/* Tło - blokujemy klikanie w tło podczas ładowania */}
            <div className="absolute inset-0 bg-gray-900/40 backdrop-blur-sm transition-opacity" onClick={!isSubmitting ? onClose : undefined}></div>

            <div className="bg-white rounded-2xl shadow-2xl w-full max-w-lg relative z-10 overflow-hidden max-h-[90vh] overflow-y-auto">
                <div className="flex justify-between items-center p-6 border-b border-gray-100 sticky top-0 bg-white z-20">
                    <h3 className="text-xl font-bold text-gray-800">
                        {employee ? 'Edycja danych' : 'Rejestracja pracownika'}
                    </h3>
                    {/* Przycisk X zablokowany podczas ładowania */}
                    <button
                        onClick={onClose}
                        disabled={isSubmitting}
                        className="text-gray-400 hover:text-gray-600 p-2 rounded-full cursor-pointer disabled:opacity-30"
                    >
                        <X size={20} />
                    </button>
                </div>

                <form ref={formRef} className="p-6 space-y-5">
                    {/* Upload Zdjęć */}
                    <div className="space-y-2">
                        <label className="text-xs font-semibold text-gray-500 uppercase flex justify-between">
                            <span>Zdjęcia referencyjne</span>
                            <span className="text-indigo-600 font-bold">{formData.photoFiles.length} wybrano</span>
                        </label>

                        <div
                            onClick={() => !isSubmitting && fileInputRef.current.click()}
                            className={`border-2 border-dashed border-gray-300 rounded-xl p-4 flex flex-col items-center justify-center text-gray-500 transition-all group ${!isSubmitting ? 'hover:bg-gray-50 hover:border-indigo-400 cursor-pointer' : 'opacity-50 cursor-not-allowed'}`}
                        >
                            <div className="bg-gray-100 p-2 rounded-full mb-2 group-hover:bg-indigo-50 group-hover:text-indigo-600 transition-colors">
                                <UploadCloud size={20} />
                            </div>
                            <p className="text-sm font-medium">Kliknij, aby dodać zdjęcia</p>
                            <p className="text-xs text-gray-400">Możesz wybrać wiele plików naraz</p>
                        </div>

                        {formData.photoPreviews.length > 0 && (
                            <div className="grid grid-cols-4 gap-2 mt-3">
                                {formData.photoPreviews.map((src, index) => (
                                    <div key={index} className="relative group aspect-square rounded-lg overflow-hidden border border-gray-200">
                                        <img src={src} alt="Podgląd" className="w-full h-full object-cover" />
                                        {!isSubmitting && (
                                            <div className="absolute inset-0 bg-black/40 opacity-0 group-hover:opacity-100 transition-opacity flex items-center justify-center">
                                                <button
                                                    type="button"
                                                    onClick={(e) => { e.stopPropagation(); handleRemovePhoto(index); }}
                                                    className="bg-red-500 text-white p-1.5 rounded-full hover:bg-red-600 transition-colors cursor-pointer"
                                                >
                                                    <Trash2 size={14} />
                                                </button>
                                            </div>
                                        )}
                                    </div>
                                ))}
                            </div>
                        )}

                        <input
                            type="file"
                            ref={fileInputRef}
                            onChange={handleFileChange}
                            accept="image/*"
                            className="hidden"
                            multiple
                            disabled={isSubmitting}
                        />
                    </div>

                    {/* Pola tekstowe - zablokowane podczas wysyłania */}
                    <div className="grid grid-cols-2 gap-4">
                        <div className="space-y-1">
                            <label className="text-xs font-semibold text-gray-500 uppercase">Imię *</label>
                            <input disabled={isSubmitting} type="text" value={formData.firstName} onChange={(e) => setFormData({ ...formData, firstName: e.target.value })} className="w-full px-4 py-2 bg-gray-50 border border-gray-200 rounded-xl outline-none focus:ring-2 focus:ring-indigo-500/20 disabled:bg-gray-100" />
                        </div>
                        <div className="space-y-1">
                            <label className="text-xs font-semibold text-gray-500 uppercase">Nazwisko *</label>
                            <input disabled={isSubmitting} type="text" value={formData.lastName} onChange={(e) => setFormData({ ...formData, lastName: e.target.value })} className="w-full px-4 py-2 bg-gray-50 border border-gray-200 rounded-xl outline-none focus:ring-2 focus:ring-indigo-500/20 disabled:bg-gray-100" />
                        </div>
                    </div>

                    <div className="space-y-1">
                        <label className="text-xs font-semibold text-gray-500 uppercase flex items-center gap-1"><Mail size={12} /> Email *</label>
                        <input disabled={isSubmitting} type="email" value={formData.email} onChange={(e) => setFormData({ ...formData, email: e.target.value })} className="w-full px-4 py-2 bg-gray-50 border border-gray-200 rounded-xl outline-none focus:ring-2 focus:ring-indigo-500/20 disabled:bg-gray-100" />
                    </div>

                    <div className="grid grid-cols-2 gap-4">
                        <div className="space-y-1">
                            <label className="text-xs font-semibold text-gray-500 uppercase">Stanowisko</label>
                            <input disabled={isSubmitting} type="text" value={formData.position} onChange={(e) => setFormData({ ...formData, position: e.target.value })} className="w-full px-4 py-2 bg-gray-50 border border-gray-200 rounded-xl outline-none focus:ring-2 focus:ring-indigo-500/20 disabled:bg-gray-100" />
                        </div>
                        <div className="space-y-1">
                            <label className="text-xs font-semibold text-gray-500 uppercase flex items-center gap-1"><Calendar size={12} /> Data zatrudnienia *</label>
                            <input disabled={isSubmitting} type="date" value={formData.hireDate} onChange={(e) => setFormData({ ...formData, hireDate: e.target.value })} className="w-full px-4 py-2 bg-gray-50 border border-gray-200 rounded-xl outline-none focus:ring-2 focus:ring-indigo-500/20 disabled:bg-gray-100" />
                        </div>
                    </div>

                    <div className="pt-4 flex gap-3">
                        <button
                            type="button"
                            onClick={onClose}
                            disabled={isSubmitting}
                            className="flex-1 px-4 py-2 border border-gray-200 text-gray-600 rounded-xl hover:bg-gray-50 font-medium cursor-pointer disabled:opacity-50"
                        >
                            Anuluj
                        </button>

                        {/* Zmieniono typ na 'button' i dodano onClick */}
                        <button
                            type="button"
                            onClick={handleManualSubmit}
                            disabled={isSubmitting}
                            className={`flex-1 px-4 py-2 text-white rounded-xl font-medium shadow-lg shadow-indigo-200 cursor-pointer flex items-center justify-center gap-2 transition-all ${isSubmitting ? 'bg-indigo-400 cursor-wait' : 'bg-indigo-600 hover:bg-indigo-700'}`}
                        >
                            {isSubmitting ? (
                                <>
                                    <RefreshCw className="animate-spin" size={20} />
                                    <span>Trenowanie AI...</span>
                                </>
                            ) : (
                                employee ? 'Zapisz zmiany' : `Zapisz i wgraj (${formData.photoFiles.length})`
                            )}
                        </button>
                    </div>
                </form>
            </div>
        </div>
    );
};

export default EmployeeModal;