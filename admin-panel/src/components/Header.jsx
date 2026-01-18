import React from 'react';
import { Layers, Bell, Search } from 'lucide-react';

const Header = () => {
    return (
        <header className="bg-white border-b border-gray-100 sticky top-0 z-30">
            <div className="max-w-6xl mx-auto px-6 h-16 flex items-center justify-between">
                {/* Logo Area */}
                <div className="flex items-center gap-3">
                    <div className="bg-indigo-600 p-2 rounded-lg text-white shadow-md shadow-indigo-200">
                        <Layers size={20} strokeWidth={3} />
                    </div>
                    <span className="text-xl font-bold bg-clip-text text-transparent bg-gradient-to-r from-gray-900 to-gray-600">
                        AdminPanel
                    </span>
                </div>

                {/* Right Actions */}
                <div className="flex items-center gap-4">
                    <div className="hidden md:flex items-center px-3 py-1.5 bg-gray-50 rounded-lg border border-gray-100 focus-within:border-indigo-300 focus-within:ring-2 focus-within:ring-indigo-100 transition-all">
                        <Search size={16} className="text-gray-400" />
                        <input
                            type="text"
                            placeholder="Szukaj..."
                            className="bg-transparent border-none focus:outline-none text-sm ml-2 w-48 text-gray-600 placeholder-gray-400"
                        />
                    </div>

                    <button className="relative p-2 text-gray-400 hover:text-indigo-600 hover:bg-indigo-50 rounded-full transition-colors cursor-pointer">
                        <Bell size={20} />
                        <span className="absolute top-2 right-2 w-2 h-2 bg-red-500 rounded-full ring-2 ring-white"></span>
                    </button>

                    <div className="w-8 h-8 rounded-full bg-gradient-to-tr from-indigo-500 to-purple-500 text-white flex items-center justify-center text-xs font-bold ring-2 ring-white shadow-md cursor-pointer">
                        AD
                    </div>
                </div>
            </div>
        </header>
    );
};

export default Header;