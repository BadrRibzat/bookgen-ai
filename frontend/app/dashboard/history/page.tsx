'use client';

import React, { useState, useEffect } from 'react';
import DashboardLayout from '@/components/dashboard/DashboardLayout';
import { getBookHistory, deleteBook } from '@/lib/api/books';
import { Book } from '@/shared/types';
import {
    BookOpen,
    Trash2,
    Clock,
    CheckCircle2,
    AlertCircle,
    Search,
    Filter,
    ExternalLink
} from 'lucide-react';
import { format } from 'date-fns';

const BookHistoryPage = () => {
    const [books, setBooks] = useState<Book[]>([]);
    const [loading, setLoading] = useState(true);
    const [search, setSearch] = useState('');
    const [statusFilter, setStatusFilter] = useState<'all' | 'completed' | 'processing' | 'failed'>('all');

    const fetchHistory = async () => {
        setLoading(true);
        try {
            const data = await getBookHistory();
            setBooks(data.results || []);
        } catch (err) {
            console.error('Failed to fetch book history', err);
        } finally {
            setLoading(false);
        }
    };

    useEffect(() => {
        fetchHistory();
    }, []);

    const handleDelete = async (id: string) => {
        if (window.confirm('Are you sure you want to delete this book?')) {
            try {
                await deleteBook(id);
                setBooks(books.filter(b => b.id !== id));
            } catch (err) {
                console.error('Failed to delete book', err);
            }
        }
    };

    const filteredBooks = books.filter(book => {
        const matchesSearch = book.title.toLowerCase().includes(search.toLowerCase());
        const matchesStatus = statusFilter === 'all' || book.status === statusFilter;
        return matchesSearch && matchesStatus;
    });

    const getStatusBadge = (status: string) => {
        switch (status) {
            case 'completed':
                return (
                    <div className="flex items-center space-x-1.5 text-emerald-500 bg-emerald-500/10 px-3 py-1 rounded-full text-xs font-black uppercase tracking-wider">
                        <CheckCircle2 className="w-3.5 h-3.5" />
                        <span>Success</span>
                    </div>
                );
            case 'processing':
                return (
                    <div className="flex items-center space-x-1.5 text-amber-500 bg-amber-500/10 px-3 py-1 rounded-full text-xs font-black uppercase tracking-wider animate-pulse">
                        <Clock className="w-3.5 h-3.5" />
                        <span>Generating</span>
                    </div>
                );
            case 'failed':
                return (
                    <div className="flex items-center space-x-1.5 text-rose-500 bg-rose-500/10 px-3 py-1 rounded-full text-xs font-black uppercase tracking-wider">
                        <AlertCircle className="w-3.5 h-3.5" />
                        <span>Failed</span>
                    </div>
                );
            default:
                return (
                    <div className="flex items-center space-x-1.5 text-slate-500 bg-slate-500/10 px-3 py-1 rounded-full text-xs font-black uppercase tracking-wider">
                        <span>Pending</span>
                    </div>
                );
        }
    };

    return (
        <DashboardLayout>
            <div className="space-y-8 animate-fade-in">
                <div className="flex flex-col md:flex-row md:items-end justify-between gap-6">
                    <div>
                        <h2 className="text-4xl font-black text-slate-900 dark:text-white mb-2 tracking-tight">My Library</h2>
                        <p className="text-slate-500 font-medium">Manage and explore your generated collections.</p>
                    </div>

                    <div className="flex items-center space-x-4">
                        <div className="relative group">
                            <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-slate-400 group-focus-within:text-indigo-500 transition-colors" />
                            <input
                                type="text"
                                placeholder="Search by title..."
                                value={search}
                                onChange={(e) => setSearch(e.target.value)}
                                className="pl-10 pr-4 py-3 bg-white dark:bg-slate-800 border-2 border-transparent focus:border-indigo-500 rounded-2xl outline-none transition-all shadow-sm w-full md:w-64 font-medium"
                            />
                        </div>

                        <div className="relative">
                            <div className="absolute left-3 top-1/2 -translate-y-1/2">
                                <Filter className="w-4 h-4 text-slate-400" />
                            </div>
                            <select
                                value={statusFilter}
                                onChange={(e) => setStatusFilter(e.target.value as any)}
                                className="pl-9 pr-8 py-3 bg-white dark:bg-slate-800 border-2 border-transparent focus:border-indigo-500 rounded-2xl outline-none transition-all shadow-sm font-bold text-slate-600 dark:text-slate-300 appearance-none cursor-pointer"
                            >
                                <option value="all">All Status</option>
                                <option value="completed">Success</option>
                                <option value="processing">Generating</option>
                                <option value="failed">Failed</option>
                            </select>
                        </div>
                    </div>
                </div>

                {loading ? (
                    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
                        {[1, 2, 3].map(i => (
                            <div key={i} className="bg-white dark:bg-slate-800 h-80 rounded-[2.5rem] border-2 border-slate-100 dark:border-slate-800 animate-pulse"></div>
                        ))}
                    </div>
                ) : filteredBooks.length > 0 ? (
                    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
                        {filteredBooks.map((book) => (
                            <div
                                key={book.id}
                                className="group bg-white dark:bg-slate-900 rounded-[2.5rem] border-2 border-slate-100 dark:border-slate-800 hover:border-indigo-500/50 transition-all duration-300 shadow-sm hover:shadow-2xl overflow-hidden relative flex flex-col"
                            >
                                {/* Book Cover / Placeholder */}
                                <div className="h-44 bg-gradient-to-br from-indigo-500/5 to-violet-500/5 flex items-center justify-center relative group-hover:scale-105 transition-transform duration-500">
                                    <div className="w-24 h-32 bg-white dark:bg-slate-800 rounded-lg shadow-2xl flex items-center justify-center p-4 transform -rotate-3 group-hover:rotate-0 transition-transform border border-slate-100 dark:border-slate-700">
                                        <BookOpen className="w-12 h-12 text-slate-200 dark:text-slate-700" />
                                    </div>
                                    <div className="absolute top-4 right-4">
                                        {getStatusBadge(book.status)}
                                    </div>
                                </div>

                                {/* Content */}
                                <div className="p-8 flex-1 flex flex-col">
                                    <h3 className="text-xl font-black text-slate-900 dark:text-white mb-3 line-clamp-2 leading-tight">
                                        {book.title}
                                    </h3>

                                    <div className="flex items-center text-xs font-bold text-slate-400 uppercase tracking-widest space-x-3 mb-6">
                                        <span>{format(new Date(book.created_at), 'MMM dd, yyyy')}</span>
                                        <span className="w-1.5 h-1.5 bg-slate-200 dark:bg-slate-800 rounded-full"></span>
                                        <span className="text-indigo-500">{book.domain_id}</span>
                                    </div>

                                    <div className="mt-auto flex items-center justify-between gap-3">
                                        <button
                                            className="flex-1 bg-slate-900 dark:bg-slate-800 text-white dark:text-slate-300 font-black py-3 rounded-2xl hover:bg-slate-800 dark:hover:bg-slate-700 transition-colors flex items-center justify-center space-x-2 text-sm shadow-xl"
                                            disabled={book.status !== 'completed'}
                                        >
                                            <ExternalLink className="w-4 h-4" />
                                            <span>Open Reader</span>
                                        </button>

                                        <button
                                            onClick={() => handleDelete(book.id)}
                                            className="p-3 bg-rose-500/5 text-rose-500 hover:bg-rose-500 hover:text-white rounded-2xl transition-all border border-rose-500/10"
                                        >
                                            <Trash2 className="w-5 h-5" />
                                        </button>
                                    </div>
                                </div>
                            </div>
                        ))}
                    </div>
                ) : (
                    <div className="bg-white dark:bg-slate-900/50 rounded-[3rem] p-20 text-center border-2 border-dashed border-slate-200 dark:border-slate-800">
                        <div className="w-24 h-24 bg-slate-50 dark:bg-slate-800 rounded-full flex items-center justify-center mx-auto mb-8">
                            <BookOpen className="w-12 h-12 text-slate-300" />
                        </div>
                        <h3 className="text-2xl font-black text-slate-900 dark:text-white mb-3">No Books Found</h3>
                        <p className="text-slate-500 max-w-sm mx-auto mb-8 font-medium italic">
                            "Your story begins on a blank page. Unfortunately, your library is a bit too blank right now."
                        </p>
                        <button
                            onClick={() => window.location.href = '/dashboard/generate'}
                            className="bg-indigo-600 hover:bg-indigo-700 text-white font-black px-10 py-4 rounded-3xl shadow-2xl shadow-indigo-600/20 active:scale-95 transition-all"
                        >
                            Start Your First Book
                        </button>
                    </div>
                )}
            </div>
        </DashboardLayout>
    );
};

export default BookHistoryPage;
