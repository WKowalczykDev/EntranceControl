import React from 'react';
import { X, Download, Printer, QrCode } from 'lucide-react';

const QrCodeModal = ({ isOpen, onClose, qrUrl, employeeName }) => {
    if (!isOpen || !qrUrl) return null;

    const handleDownload = () => {
        const link = document.createElement('a');
        link.href = qrUrl;
        link.download = `QR_Przepustka_${employeeName.replace(/\s+/g, '_')}.png`;
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
    };

    return (
        <div className="fixed inset-0 z-[60] flex items-center justify-center p-4">
            {/* Tło z rozmyciem */}
            <div className="absolute inset-0 bg-black/60 backdrop-blur-sm transition-opacity" onClick={onClose}></div>

            {/* Karta Modala */}
            <div className="bg-white rounded-2xl shadow-2xl w-full max-w-sm relative z-10 overflow-hidden transform transition-all scale-100 animate-in fade-in zoom-in duration-200">
                <div className="bg-gray-900 p-6 text-white text-center relative">
                    <button
                        onClick={onClose}
                        className="absolute top-4 right-4 text-gray-400 hover:text-white transition-colors cursor-pointer"
                    >
                        <X size={24} />
                    </button>
                    <div className="flex justify-center mb-3">
                        <div className="bg-white/10 p-3 rounded-full">
                            <QrCode size={32} />
                        </div>
                    </div>
                    <h3 className="text-lg font-bold">Przepustka QR</h3>
                    <p className="text-gray-400 text-sm mt-1">{employeeName}</p>
                </div>

                <div className="p-8 flex flex-col items-center">
                    <div className="bg-white p-2 rounded-xl shadow-inner border border-gray-200">
                        <img
                            src={qrUrl}
                            alt="Kod QR"
                            className="w-48 h-48 object-contain"
                        />
                    </div>
                    <p className="text-xs text-gray-400 mt-4 text-center">
                        Zeskanuj ten kod przy bramce wejściowej.<br/>
                        Ważny przez 1 rok.
                    </p>
                </div>

                <div className="p-4 border-t border-gray-100 bg-gray-50 flex gap-3">
                    <button
                        onClick={handleDownload}
                        className="flex-1 flex items-center justify-center gap-2 bg-indigo-600 text-white px-4 py-2.5 rounded-xl hover:bg-indigo-700 font-medium transition-colors cursor-pointer shadow-lg shadow-indigo-200"
                    >
                        <Download size={18} /> Pobierz
                    </button>
                    <button
                        onClick={() => window.print()}
                        className="flex items-center justify-center gap-2 bg-white border border-gray-300 text-gray-700 px-4 py-2.5 rounded-xl hover:bg-gray-100 font-medium transition-colors cursor-pointer"
                    >
                        <Printer size={18} />
                    </button>
                </div>
            </div>
        </div>
    );
};

export default QrCodeModal;