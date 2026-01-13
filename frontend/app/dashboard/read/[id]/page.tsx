'use client';

import React, { useState, useEffect } from 'react';
import { useParams, useRouter } from 'next/navigation';
import DashboardLayout from '@/components/dashboard/DashboardLayout';
import { getBookPreview } from '@/lib/api/books';
import {
    ArrowLeft,
    Download,
    BookOpen,
    Eye,
    FileText,
    Loader2
} from 'lucide-react';

interface BookContent {
    id: string;
    title: string;
    content: string;
    chapters?: Array<{
        title: string;
        content: string;
    }>;
    word_count?: number;
    status: string;
    created_at: string;
}

const BookReaderPage = () => {
    const params = useParams();
    const router = useRouter();
    const bookId = params.id as string;

    const [book, setBook] = useState<BookContent | null>(null);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState('');

    useEffect(() => {
        const fetchBook = async () => {
            try {
                const data = await getBookPreview(bookId);
                // Combine generation request metadata with book content
                const bookData: BookContent = {
                    ...data.generation_request,
                    content: data.book_content?.content || '',
                    chapters: data.book_content?.chapters || []
                };
                setBook(bookData);
            } catch (err: any) {
                setError(err.response?.data?.error || 'Failed to load book');
            } finally {
                setLoading(false);
            }
        };

        if (bookId) {
            fetchBook();
        }
    }, [bookId]);

    const handleDownload = async () => {
        if (!book?.pdf_url) {
            alert('PDF is not yet available. Please wait for generation to complete.');
            return;
        }

        try {
            // Create a temporary link to download the PDF
            const link = document.createElement('a');
            link.href = book.pdf_url;
            link.download = `${book.title.replace(/[^a-z0-9]/gi, '_').toLowerCase()}.pdf`;
            link.target = '_blank';
            document.body.appendChild(link);
            link.click();
            document.body.removeChild(link);
        } catch (err) {
            console.error('Download failed:', err);
            alert('Failed to download PDF. Please try again.');
        }
    };

    if (loading) {
        return (
            <DashboardLayout>
                <div className="min-h-screen flex items-center justify-center">
                    <div className="flex flex-col items-center space-y-4">
                        <Loader2 className="w-12 h-12 animate-spin text-indigo-600" />
                        <p className="text-slate-600 font-medium">Loading your book...</p>
                    </div>
                </div>
            </DashboardLayout>
        );
    }

    if (error || !book) {
        return (
            <DashboardLayout>
                <div className="min-h-screen flex items-center justify-center">
                    <div className="bg-white dark:bg-slate-900 rounded-3xl p-12 text-center max-w-md mx-auto border border-slate-200 dark:border-slate-800">
                        <div className="w-20 h-20 bg-rose-100 dark:bg-rose-900/20 rounded-full flex items-center justify-center mx-auto mb-6">
                            <FileText className="w-10 h-10 text-rose-600" />
                        </div>
                        <h2 className="text-2xl font-black text-slate-900 dark:text-white mb-4">Book Not Found</h2>
                        <p className="text-slate-500 mb-8">{error || 'This book could not be loaded.'}</p>
                        <button
                            onClick={() => router.push('/dashboard/history')}
                            className="bg-indigo-600 hover:bg-indigo-700 text-white font-black px-8 py-4 rounded-2xl transition-all"
                        >
                            Back to Library
                        </button>
                    </div>
                </div>
            </DashboardLayout>
        );
    }

    return (
        <DashboardLayout>
            <div className="min-h-screen bg-slate-50 dark:bg-slate-900">
                {/* Header */}
                <div className="bg-white dark:bg-slate-900 border-b border-slate-200 dark:border-slate-800 sticky top-0 z-10">
                    <div className="max-w-4xl mx-auto px-6 py-4">
                        <div className="flex items-center justify-between">
                            <button
                                onClick={() => router.push('/dashboard/history')}
                                className="flex items-center space-x-3 text-slate-600 hover:text-slate-900 dark:text-slate-400 dark:hover:text-white transition-colors"
                            >
                                <ArrowLeft className="w-5 h-5" />
                                <span className="font-bold">Back to Library</span>
                            </button>

                            <div className="flex items-center space-x-4">
                                <div className="flex items-center space-x-2 text-sm text-slate-500">
                                    <Eye className="w-4 h-4" />
                                    <span>Preview Mode</span>
                                </div>
                                <button
                                    onClick={handleDownload}
                                    className="bg-indigo-600 hover:bg-indigo-700 text-white font-black px-6 py-3 rounded-2xl transition-all flex items-center space-x-2 shadow-lg"
                                >
                                    <Download className="w-4 h-4" />
                                    <span>Download PDF</span>
                                </button>
                            </div>
                        </div>
                    </div>
                </div>

                {/* Book Content */}
                <div className="max-w-4xl mx-auto px-6 py-12">
                    <div className="bg-white dark:bg-slate-900 rounded-3xl shadow-2xl border border-slate-200 dark:border-slate-800 overflow-hidden">
                        {/* Book Header */}
                        <div className="bg-gradient-to-r from-indigo-600 to-violet-600 text-white p-12">
                            <div className="flex items-start space-x-8">
                                <div className="flex-shrink-0">
                                    <div className="w-24 h-32 bg-white/10 backdrop-blur-sm rounded-lg flex items-center justify-center">
                                        <BookOpen className="w-12 h-12 text-white/80" />
                                    </div>
                                </div>
                                <div className="flex-1">
                                    <h1 className="text-4xl font-black mb-4 leading-tight">{book.title}</h1>
                                    <div className="flex items-center space-x-6 text-indigo-100">
                                        <span className="flex items-center space-x-2">
                                            <FileText className="w-4 h-4" />
                                            <span>{book.word_count?.toLocaleString() || 'N/A'} words</span>
                                        </span>
                                        <span className="text-indigo-200">•</span>
                                        <span>Generated on {new Date(book.created_at).toLocaleDateString()}</span>
                                    </div>
                                </div>
                            </div>
                        </div>

                        {/* Book Content */}
                        <div className="p-12">
                            {book.chapters ? (
                                <div className="space-y-12">
                                    {book.chapters.map((chapter, index) => (
                                        <div key={index} className="chapter">
                                            <h2 className="text-2xl font-black text-slate-900 dark:text-white mb-6 border-b border-slate-200 dark:border-slate-700 pb-4">
                                                {chapter.title}
                                            </h2>
                                            <div
                                                className="prose prose-lg dark:prose-invert max-w-none text-slate-700 dark:text-slate-300 leading-relaxed"
                                                dangerouslySetInnerHTML={{ __html: chapter.content.replace(/\n/g, '<br />') }}
                                            />
                                        </div>
                                    ))}
                                </div>
                            ) : (
                                <div className="prose prose-lg dark:prose-invert max-w-none text-slate-700 dark:text-slate-300 leading-relaxed">
                                    <div dangerouslySetInnerHTML={{ __html: book.content.replace(/\n/g, '<br />') }} />
                                </div>
                            )}
                        </div>
                    </div>
                </div>
            </div>
        </DashboardLayout>
    );
};

export default BookReaderPage;