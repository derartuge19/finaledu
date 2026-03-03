"use client"

import React, { useState, useEffect } from "react"
import { motion, AnimatePresence } from "framer-motion"
import { Search, ShieldCheck, ShieldAlert, FileSearch, Upload, CheckCircle, XCircle, Info, Hash, Fingerprint, Lock, Loader2, Award, ExternalLink } from "lucide-react"
import axios from "axios"
import { Button } from "@/components/ui/button"
import Link from "next/link"
import { getApiBaseUrl } from "@/lib/api-config"

interface VerificationResult {
    summary: {
        all: boolean
        documentStatus: boolean
        documentIntegrity: boolean
        issuerIdentity: boolean
        signature: boolean
        registryCheck: boolean
    }
    data: Array<{
        type: string
        name: string
        status: string
        data?: any
    }>
    certificate?: {
        student_name: string
        course_name: string
    }
}

export default function PublicVerifyPage() {
    const [verifyId, setVerifyId] = useState("")
    const [loading, setLoading] = useState(false)
    const [result, setResult] = useState<VerificationResult | null>(null)
    const [activeMode, setActiveMode] = useState<"id" | "file">("id")
    const [dragActive, setDragActive] = useState(false)

    // Check for ID in URL params
    useEffect(() => {
        const params = new URLSearchParams(window.location.search)
        const id = params.get("id")
        if (id) {
            setVerifyId(id)
            handleVerifyId(id)
        }
    }, [])

    const handleVerifyId = async (id?: string) => {
        const certId = id || verifyId
        if (!certId) return
        setLoading(true)
        setResult(null)
        try {
            const res = await axios.post(`${getApiBaseUrl()}/api/verify`, {
                certificate_id: certId
            })
            setResult(res.data)
        } catch (err: unknown) {
            setResult(null)
            alert("Verification failed: Certificate not found.")
        } finally {
            setLoading(false)
        }
    }

    const handleFileUpload = async (file: File) => {
        setLoading(true)
        setResult(null)
        try {
            if (file.type === "application/pdf" || file.name.toLowerCase().endsWith(".pdf")) {
                const formData = new FormData()
                formData.append("file", file)
                const res = await axios.post<VerificationResult>(`${getApiBaseUrl()}/api/verify/pdf`, formData, {
                    headers: { "Content-Type": "multipart/form-data" }
                })
                setResult(res.data)
            } else {
                const text = await file.text()
                const jsonData = JSON.parse(text)
                const res = await axios.post<VerificationResult>(`${getApiBaseUrl()}/api/verify`, {
                    data_payload: jsonData
                })
                setResult(res.data)
            }
        } catch (err: any) {
            setResult(null)
            const errorMsg = err.response?.data?.detail || err.message || "Invalid document format."
            alert(`Verification failed: ${errorMsg}`)
        } finally {
            setLoading(false)
        }
    }

    const handleDrag = (e: React.DragEvent) => {
        e.preventDefault()
        e.stopPropagation()
        if (e.type === "dragenter" || e.type === "dragover") {
            setDragActive(true)
        } else if (e.type === "dragleave") {
            setDragActive(false)
        }
    }

    const handleDrop = (e: React.DragEvent) => {
        e.preventDefault()
        e.stopPropagation()
        setDragActive(false)
        if (e.dataTransfer.files && e.dataTransfer.files[0]) {
            handleFileUpload(e.dataTransfer.files[0])
        }
    }

    const FragmentStatus = ({ label, isValid }: { label: string, isValid: boolean }) => (
        <div className="flex items-center justify-between">
            <span className="text-xs text-slate-400 flex items-center gap-2">
                <div className={`w-1.5 h-1.5 rounded-full ${isValid ? "bg-emerald-500" : "bg-red-500"}`} />
                {label}
            </span>
            {isValid ? <CheckCircle className="w-4 h-4 text-emerald-500" /> : <XCircle className="w-4 h-4 text-red-500" />}
        </div>
    )

    return (
        <div className="min-h-screen bg-gradient-to-br from-slate-50 to-indigo-50">
            {/* Header */}
            <header className="bg-white border-b border-slate-200 sticky top-0 z-50">
                <div className="max-w-6xl mx-auto px-6 h-16 flex items-center justify-between">
                    <Link href="/" className="flex items-center gap-3">
                        <div className="w-10 h-10 bg-indigo-600 rounded-xl flex items-center justify-center shadow-lg shadow-indigo-600/20">
                            <Award className="w-6 h-6 text-white" />
                        </div>
                        <div>
                            <h1 className="font-bold text-lg tracking-tight text-slate-900">EduCerts<span className="text-indigo-600">.io</span></h1>
                            <p className="text-[10px] text-slate-500 uppercase tracking-widest font-semibold">Public Verification Portal</p>
                        </div>
                    </Link>
                    <div className="flex items-center gap-4">
                        <Link 
                            href="/login" 
                            className="text-sm font-semibold text-slate-600 hover:text-indigo-600 transition-colors"
                        >
                            Sign In
                        </Link>
                        <Link 
                            href="/wallet" 
                            className="px-4 py-2 bg-indigo-600 hover:bg-indigo-700 text-white text-sm font-semibold rounded-xl transition-colors shadow-lg shadow-indigo-600/20"
                        >
                            Student Wallet
                        </Link>
                    </div>
                </div>
            </header>

            <main className="p-8 max-w-4xl mx-auto space-y-12">
                <div className="text-center space-y-4 pt-8">
                    <motion.div
                        initial={{ scale: 0.8, opacity: 0 }}
                        animate={{ scale: 1, opacity: 1 }}
                        className="w-20 h-20 bg-white rounded-3xl flex items-center justify-center mx-auto mb-6 shadow-xl border border-slate-100"
                    >
                        <ShieldCheck className="w-10 h-10 text-indigo-600" />
                    </motion.div>
                    <h1 className="text-4xl font-bold text-slate-900 tracking-tight">Verify Any Credential</h1>
                    <p className="text-slate-500 max-w-xl mx-auto font-medium text-lg">
                        Instantly verify the authenticity of any EduCerts credential using our OpenAttestation-powered verification system.
                    </p>
                </div>

                <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
                    <div className="space-y-6">
                        <div className="flex gap-2 p-1 bg-white border border-slate-200 rounded-xl shadow-sm">
                            <button
                                onClick={() => setActiveMode("id")}
                                className={`flex-1 flex items-center justify-center gap-2 py-3 rounded-lg text-sm font-semibold transition-all ${activeMode === "id" ? "bg-indigo-600 text-white shadow-md" : "text-slate-500 hover:text-slate-700"}`}
                            >
                                <Hash className="w-4 h-4" />
                                By Certificate ID
                            </button>
                            <button
                                onClick={() => setActiveMode("file")}
                                className={`flex-1 flex items-center justify-center gap-2 py-3 rounded-lg text-sm font-semibold transition-all ${activeMode === "file" ? "bg-indigo-600 text-white shadow-md" : "text-slate-500 hover:text-slate-700"}`}
                            >
                                <Upload className="w-4 h-4" />
                                By Document
                            </button>
                        </div>

                        <AnimatePresence mode="wait">
                            {activeMode === "id" ? (
                                <motion.div
                                    key="id"
                                    initial={{ opacity: 0, x: -10 }}
                                    animate={{ opacity: 1, x: 0 }}
                                    exit={{ opacity: 0, x: 10 }}
                                    className="bg-white rounded-3xl shadow-xl shadow-slate-200/50 border border-slate-100 overflow-hidden"
                                >
                                    <div className="h-2 bg-indigo-600"></div>
                                    <div className="p-8 space-y-6">
                                        <div>
                                            <h3 className="text-lg font-bold text-slate-900 mb-2">Verify by ID</h3>
                                            <p className="text-sm text-slate-500">Enter the unique certificate UUID found on the credential.</p>
                                        </div>
                                        <div className="relative">
                                            <Fingerprint className="absolute left-4 top-1/2 -translate-y-1/2 w-5 h-5 text-slate-400" />
                                            <input
                                                type="text"
                                                placeholder="Paste Certificate ID..."
                                                value={verifyId}
                                                onChange={(e) => setVerifyId(e.target.value)}
                                                onKeyDown={(e) => e.key === "Enter" && handleVerifyId()}
                                                className="w-full bg-slate-50 border-2 border-slate-100 rounded-2xl px-12 py-4 text-slate-900 font-mono text-sm focus:ring-4 focus:ring-indigo-600/10 outline-none focus:border-indigo-600 font-semibold transition-all"
                                            />
                                        </div>
                                        <Button 
                                            onClick={() => handleVerifyId()} 
                                            disabled={loading || !verifyId} 
                                            className="w-full bg-indigo-600 hover:bg-indigo-700 h-14 rounded-2xl font-bold text-lg shadow-xl shadow-indigo-600/20 transition-all active:scale-95"
                                        >
                                            {loading ? <Loader2 className="w-6 h-6 animate-spin" /> : "Verify Authenticity"}
                                        </Button>
                                    </div>
                                </motion.div>
                            ) : (
                                <motion.div
                                    key="file"
                                    initial={{ opacity: 0, x: 10 }}
                                    animate={{ opacity: 1, x: 0 }}
                                    exit={{ opacity: 0, x: -10 }}
                                >
                                    <div
                                        onDragEnter={handleDrag}
                                        onDragLeave={handleDrag}
                                        onDragOver={handleDrag}
                                        onDrop={handleDrop}
                                        className={`h-[280px] border-3 border-dashed rounded-3xl flex flex-col items-center justify-center gap-6 transition-all shadow-xl ${dragActive ? "border-indigo-600 bg-indigo-50 shadow-indigo-600/20" : "border-slate-200 bg-white"}`}
                                    >
                                        <div className="w-16 h-16 bg-indigo-50 rounded-2xl flex items-center justify-center border border-indigo-100">
                                            <FileSearch className="w-8 h-8 text-indigo-600" />
                                        </div>
                                        <div className="text-center">
                                            <p className="text-lg font-bold text-slate-900 mb-1">Drop your document here</p>
                                            <p className="text-sm text-slate-400 font-medium">Supports PDF and JSON files</p>
                                        </div>
                                        <input
                                            type="file"
                                            accept=".json,.pdf"
                                            className="hidden"
                                            id="file-verify"
                                            onChange={(e) => e.target.files && handleFileUpload(e.target.files[0])}
                                        />
                                        <label 
                                            htmlFor="file-verify" 
                                            className="px-6 py-3 bg-slate-100 hover:bg-slate-200 text-slate-700 rounded-xl cursor-pointer font-semibold transition-colors"
                                        >
                                            Browse Files
                                        </label>
                                    </div>
                                </motion.div>
                            )}
                        </AnimatePresence>

                        <div className="p-6 bg-amber-50 rounded-2xl border border-amber-200 flex gap-4">
                            <Info className="w-6 h-6 text-amber-600 shrink-0" />
                            <div className="text-sm text-amber-800 leading-relaxed">
                                <p className="font-bold mb-1">How it works:</p>
                                <p>We verify the document&apos;s Merkle proof, validate the Ed25519 signature, and check the Document Registry to ensure authenticity.</p>
                            </div>
                        </div>
                    </div>

                    <div className="relative">
                        <AnimatePresence mode="wait">
                            {!result ? (
                                <motion.div
                                    initial={{ opacity: 0 }}
                                    animate={{ opacity: 1 }}
                                    className="h-full flex flex-col items-center justify-center space-y-6 border-2 border-dashed border-slate-200 rounded-3xl bg-white/50 p-12"
                                >
                                    <div className="w-24 h-24 bg-slate-100 rounded-full flex items-center justify-center">
                                        <ShieldCheck className="w-12 h-12 text-slate-300" />
                                    </div>
                                    <div className="text-center">
                                        <p className="text-slate-400 font-bold uppercase tracking-widest text-sm">Ready to Verify</p>
                                        <p className="text-slate-300 text-sm mt-2">Enter a certificate ID or upload a document</p>
                                    </div>
                                </motion.div>
                            ) : (
                                <motion.div
                                    initial={{ opacity: 0, scale: 0.95 }}
                                    animate={{ opacity: 1, scale: 1 }}
                                    className={`p-8 rounded-3xl border-2 h-full flex flex-col shadow-xl ${result.summary.all ? "bg-white border-emerald-200" : "bg-white border-red-200"}`}
                                >
                                    <div className={`h-2 -mx-8 -mt-8 mb-8 rounded-t-3xl ${result.summary.all ? "bg-emerald-500" : "bg-red-500"}`}></div>
                                    <div className="flex items-center gap-4 mb-8">
                                        <div className={`w-16 h-16 rounded-2xl flex items-center justify-center ${result.summary.all ? "bg-emerald-500 text-white shadow-lg shadow-emerald-500/20" : "bg-red-500 text-white shadow-lg shadow-red-500/20"}`}>
                                            {result.summary.all ? <ShieldCheck className="w-8 h-8" /> : <ShieldAlert className="w-8 h-8" />}
                                        </div>
                                        <div>
                                            <h3 className={`text-2xl font-bold ${result.summary.all ? "text-emerald-700" : "text-red-700"}`}>
                                                {result.summary.all ? "Fully Verified" : "Verification Failed"}
                                            </h3>
                                            <p className={`text-sm font-medium ${result.summary.all ? "text-emerald-600" : "text-red-600"}`}>
                                                {result.summary.all ? "The credential is legitimate and intact." : "Integrity or identity check failed."}
                                            </p>
                                        </div>
                                    </div>

                                    <div className="flex-1 space-y-6">
                                        {result.summary.all && (
                                            <div className="grid grid-cols-2 gap-4 p-6 bg-slate-50 rounded-2xl border border-slate-100">
                                                <div className="space-y-1">
                                                    <p className="text-[10px] text-slate-400 uppercase font-bold tracking-widest">Student</p>
                                                    <p className="text-sm font-bold text-slate-900">{result.certificate?.student_name || "N/A"}</p>
                                                </div>
                                                <div className="space-y-1">
                                                    <p className="text-[10px] text-slate-400 uppercase font-bold tracking-widest">Course</p>
                                                    <p className="text-sm font-bold text-slate-900">{result.certificate?.course_name || "N/A"}</p>
                                                </div>
                                            </div>
                                        )}

                                        <div className="space-y-4 pt-4">
                                            <p className="text-xs font-bold text-slate-400 uppercase tracking-widest">Verification Checks</p>
                                            <div className="space-y-3">
                                                <FragmentStatus label="Document Integrity" isValid={result.summary.documentIntegrity} />
                                                <FragmentStatus label="Issuance Status" isValid={result.summary.documentStatus} />
                                                <FragmentStatus label="Issuer Identity" isValid={result.summary.issuerIdentity} />
                                                <FragmentStatus label="Registry Verification" isValid={result.summary.registryCheck} />
                                                <FragmentStatus label="Cryptographic Signature" isValid={result.summary.signature} />
                                            </div>
                                        </div>

                                        <div className="mt-auto pt-6">
                                            <button 
                                                onClick={() => setResult(null)} 
                                                className="w-full py-4 rounded-2xl bg-slate-100 hover:bg-slate-200 text-slate-600 text-sm font-bold transition-all"
                                            >
                                                Clear Result
                                            </button>
                                        </div>
                                    </div>
                                </motion.div>
                            )}
                        </AnimatePresence>
                    </div>
                </div>

                {/* Footer */}
                <div className="text-center pt-12 border-t border-slate-200">
                    <p className="text-sm text-slate-400">
                        Powered by <span className="font-semibold text-indigo-600">OpenAttestation</span> • 
                        Secured by <span className="font-semibold text-indigo-600">Ed25519</span> • 
                        Verified on <span className="font-semibold text-indigo-600">EduCerts Registry</span>
                    </p>
                </div>
            </main>
        </div>
    )
}
