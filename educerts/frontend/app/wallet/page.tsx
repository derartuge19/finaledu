"use client"

import React, { useState, useEffect } from "react"
import { useAuth } from "@/context/AuthContext"
import { motion, AnimatePresence } from "framer-motion"
import {
    Wallet,
    Plus,
    Award,
    Download,
    FileText,
    ShieldCheck,
    LogOut,
    Loader2,
    Smartphone,
    QrCode,
    ChevronRight,
    ArrowLeft,
    Share2,
    Info,
    CheckCircle2,
    Search,
    X,
    Camera,
    Copy,
    ExternalLink,
    Scan,
    DownloadCloud
} from "lucide-react"
import axios from "axios"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"
import Link from "next/link"
import dynamic from "next/dynamic"
import qrcode from "qrcode"
import { getApiBaseUrl } from "@/lib/api-config"

// Dynamically import QR Scanner to avoid SSR issues
const QRScanner = dynamic(() => import("@/components/QRScanner"), { 
    ssr: false,
    loading: () => (
        <div className="w-full aspect-square bg-slate-100 rounded-[2rem] flex items-center justify-center">
            <Loader2 className="w-8 h-8 text-slate-400 animate-spin" />
        </div>
    )
})

interface Certificate {
    id: string
    course_name: string
    student_name: string
    issued_at: string
    revoked: boolean
    organization: string
}

export default function WalletPage() {
    const { user, logout } = useAuth()
    const [activeTab, setActiveTab] = useState("wallet")
    const [claimPin, setClaimPin] = useState("")
    const [organization, setOrganization] = useState("EduCerts Academy")
    const [certs, setCerts] = useState<Certificate[]>([])
    const [loading, setLoading] = useState(true)
    const [claiming, setClaiming] = useState(false)
    const [successMessage, setSuccessMessage] = useState("")
    const [errorMessage, setErrorMessage] = useState("")
    const [selectedCert, setSelectedCert] = useState<Certificate | null>(null)
    const [showQRCode, setShowQRCode] = useState(false)
    const [qrCodeData, setQrCodeData] = useState<string>("")
    const [scanResult, setScanResult] = useState<string | null>(null)
    const [verifying, setVerifying] = useState(false)
    const [verificationResult, setVerificationResult] = useState<any>(null)
    const [deferredPrompt, setDeferredPrompt] = useState<any>(null)
    const [showInstallBanner, setShowInstallBanner] = useState(false)
    const [isInstalled, setIsInstalled] = useState(false)

    // Check if app is already installed
    useEffect(() => {
        // Check if running as installed PWA
        if (window.matchMedia('(display-mode: standalone)').matches) {
            setIsInstalled(true)
        }

        // Listen for install prompt
        const handleBeforeInstallPrompt = (e: Event) => {
            e.preventDefault()
            setDeferredPrompt(e)
            setShowInstallBanner(true)
        }

        window.addEventListener('beforeinstallprompt', handleBeforeInstallPrompt)

        // Listen for successful install
        window.addEventListener('appinstalled', () => {
            setIsInstalled(true)
            setShowInstallBanner(false)
            setDeferredPrompt(null)
        })

        return () => {
            window.removeEventListener('beforeinstallprompt', handleBeforeInstallPrompt)
        }
    }, [])

    const handleInstallClick = async () => {
        if (!deferredPrompt) return
        
        deferredPrompt.prompt()
        const { outcome } = await deferredPrompt.userChoice
        
        if (outcome === 'accepted') {
            setShowInstallBanner(false)
        }
        setDeferredPrompt(null)
    }

    useEffect(() => {
        if (user) {
            fetchClaimedCerts()
        }
    }, [user])

    const fetchClaimedCerts = async () => {
        setLoading(true)
        try {
            const res = await axios.get<Certificate[]>(`${getApiBaseUrl()}/api/certificates/${user?.name}`)
            setCerts(res.data)
        } catch (error) {
            console.error(error)
        } finally {
            setLoading(false)
        }
    }

    const handleClaim = async () => {
        if (!claimPin) return
        setClaiming(true)
        setErrorMessage("")
        try {
            const res = await axios.post(`${getApiBaseUrl()}/api/claim`, {
                pin: claimPin,
                organization: organization
            })
            setSuccessMessage(`Successfully claimed: ${res.data.course_name}`)
            setClaimPin("")
            fetchClaimedCerts()

            const newCert = res.data
            setSelectedCert(newCert)

            setTimeout(() => setSuccessMessage(""), 3000)
            setActiveTab("wallet")
        } catch (error: any) {
            setErrorMessage(error.response?.data?.detail || "Claim failed. Check your PIN.")
        } finally {
            setClaiming(false)
        }
    }

    const generateQRCode = async (certId: string) => {
        try {
            const verifyUrl = `${window.location.origin}/verify-public?id=${certId}`
            const qrDataUrl = await qrcode.toDataURL(verifyUrl, {
                width: 300,
                margin: 2,
                color: {
                    dark: "#1e293b",
                    light: "#ffffff"
                }
            })
            setQrCodeData(qrDataUrl)
            setShowQRCode(true)
        } catch (error) {
            console.error("QR generation error:", error)
        }
    }

    const handleScanSuccess = async (decodedText: string) => {
        setScanResult(decodedText)
        setVerifying(true)
        setVerificationResult(null)

        try {
            // Extract certificate ID from the scanned URL or use as-is
            let certId = decodedText
            if (decodedText.includes("?id=")) {
                certId = new URL(decodedText).searchParams.get("id") || decodedText
            } else if (decodedText.includes("/verify")) {
                const parts = decodedText.split("/")
                certId = parts[parts.length - 1]
            }

            // Verify the certificate
            const res = await axios.post(`${getApiBaseUrl()}/api/verify`, {
                certificate_id: certId
            })

            setVerificationResult(res.data)
            setSuccessMessage("Certificate verified successfully!")
            setTimeout(() => setSuccessMessage(""), 3000)
        } catch (error: any) {
            setErrorMessage(error.response?.data?.detail || "Verification failed")
            setTimeout(() => setErrorMessage(""), 3000)
        } finally {
            setVerifying(false)
        }
    }

    const copyToClipboard = (text: string) => {
        navigator.clipboard.writeText(text)
        setSuccessMessage("Copied to clipboard!")
        setTimeout(() => setSuccessMessage(""), 2000)
    }

    const shareCredential = async (cert: Certificate) => {
        const shareUrl = `${window.location.origin}/verify-public?id=${cert.id}`
        
        if (navigator.share) {
            try {
                await navigator.share({
                    title: `${cert.course_name} - EduCerts Credential`,
                    text: `Verify my credential: ${cert.course_name}`,
                    url: shareUrl
                })
            } catch (error) {
                copyToClipboard(shareUrl)
            }
        } else {
            copyToClipboard(shareUrl)
        }
    }

    return (
        <div className="min-h-screen bg-gradient-to-b from-slate-50 to-slate-100 text-slate-900 font-sans selection:bg-indigo-100">
            {/* Mobile Header */}
            <header className="fixed top-0 inset-x-0 h-16 bg-white/90 backdrop-blur-xl border-b border-slate-200 z-50 px-4 flex items-center justify-between shadow-sm safe-area-inset-top">
                <div className="flex items-center gap-3">
                    <div className="w-10 h-10 bg-gradient-to-br from-indigo-600 to-violet-600 rounded-xl flex items-center justify-center shadow-lg shadow-indigo-600/30">
                        <Wallet className="w-5 h-5 text-white" />
                    </div>
                    <div>
                        <span className="font-black tracking-tight text-lg">EduWallet</span>
                        <p className="text-[9px] text-slate-400 font-bold uppercase tracking-widest">Mobile Credential Manager</p>
                    </div>
                </div>
                <Link href="/student">
                    <button className="p-2.5 hover:bg-slate-100 rounded-xl transition-colors text-slate-400">
                        <ArrowLeft className="w-5 h-5" />
                    </button>
                </Link>
            </header>

            <main className="pt-20 pb-28 px-4 max-w-lg mx-auto mobile-safe-area">
                {/* Success/Error Messages */}
                <AnimatePresence>
                    {successMessage && (
                        <motion.div
                            initial={{ opacity: 0, y: -20, scale: 0.95 }}
                            animate={{ opacity: 1, y: 0, scale: 1 }}
                            exit={{ opacity: 0, y: -20, scale: 0.95 }}
                            className="bg-emerald-500 text-white p-4 rounded-2xl shadow-xl shadow-emerald-500/30 flex items-center gap-3 mb-4"
                        >
                            <CheckCircle2 className="w-5 h-5 shrink-0" />
                            <span className="font-bold text-sm">{successMessage}</span>
                        </motion.div>
                    )}
                    {errorMessage && (
                        <motion.div
                            initial={{ opacity: 0, y: -20, scale: 0.95 }}
                            animate={{ opacity: 1, y: 0, scale: 1 }}
                            exit={{ opacity: 0, y: -20, scale: 0.95 }}
                            className="bg-red-500 text-white p-4 rounded-2xl shadow-xl shadow-red-500/30 flex items-center gap-3 mb-4"
                        >
                            <X className="w-5 h-5 shrink-0" />
                            <span className="font-bold text-sm">{errorMessage}</span>
                        </motion.div>
                    )}
                </AnimatePresence>

                {/* Install App Banner */}
                <AnimatePresence>
                    {showInstallBanner && !isInstalled && (
                        <motion.div
                            initial={{ opacity: 0, y: -20, scale: 0.95 }}
                            animate={{ opacity: 1, y: 0, scale: 1 }}
                            exit={{ opacity: 0, y: -20, scale: 0.95 }}
                            className="bg-gradient-to-r from-indigo-600 to-violet-600 text-white p-4 rounded-2xl shadow-xl shadow-indigo-600/30 mb-4"
                        >
                            <div className="flex items-center gap-3">
                                <div className="w-12 h-12 bg-white/20 rounded-xl flex items-center justify-center">
                                    <DownloadCloud className="w-6 h-6" />
                                </div>
                                <div className="flex-1">
                                    <h3 className="font-bold text-sm">Install EduWallet</h3>
                                    <p className="text-[10px] text-white/80">Add to home screen for the best experience</p>
                                </div>
                                <div className="flex gap-2">
                                    <button
                                        onClick={() => setShowInstallBanner(false)}
                                        className="p-2 hover:bg-white/10 rounded-lg transition-colors"
                                    >
                                        <X className="w-4 h-4" />
                                    </button>
                                    <button
                                        onClick={handleInstallClick}
                                        className="px-4 py-2 bg-white text-indigo-600 rounded-xl font-bold text-xs hover:bg-white/90 transition-colors"
                                    >
                                        Install
                                    </button>
                                </div>
                            </div>
                        </motion.div>
                    )}
                </AnimatePresence>

                {/* User Profile Card */}
                <motion.div 
                    initial={{ opacity: 0, y: 20 }}
                    animate={{ opacity: 1, y: 0 }}
                    className="mb-6 flex items-center gap-4 bg-white p-5 rounded-[2rem] shadow-xl shadow-slate-200/50 border border-slate-100"
                >
                    <div className="w-14 h-14 bg-gradient-to-br from-indigo-600 to-violet-600 rounded-2xl flex items-center justify-center text-white text-xl font-black shadow-lg shadow-indigo-600/30">
                        {user?.name?.[0].toUpperCase()}
                    </div>
                    <div className="flex-1">
                        <h2 className="text-lg font-black tracking-tight text-slate-900">{user?.name}</h2>
                        <div className="flex items-center gap-2 mt-0.5">
                            <ShieldCheck className="w-3.5 h-3.5 text-emerald-500" />
                            <span className="text-[10px] text-slate-400 font-bold uppercase tracking-widest">Verified Identity</span>
                        </div>
                    </div>
                    <button
                        onClick={() => logout()}
                        className="p-3 hover:bg-red-50 rounded-xl transition-colors text-slate-300 hover:text-red-500"
                    >
                        <LogOut className="w-5 h-5" />
                    </button>
                </motion.div>

                {/* Main Tabs */}
                <Tabs value={activeTab} onValueChange={setActiveTab} className="space-y-6">
                    <TabsList className="w-full bg-white border border-slate-200 rounded-2xl h-14 p-1.5 shadow-sm">
                        <TabsTrigger
                            value="wallet"
                            className="flex-1 rounded-xl data-[state=active]:bg-indigo-600 data-[state=active]:text-white data-[state=active]:shadow-lg transition-all font-bold text-xs uppercase tracking-widest"
                        >
                            <Award className="w-4 h-4 mr-1.5" />
                            Credentials
                        </TabsTrigger>
                        <TabsTrigger
                            value="scan"
                            className="flex-1 rounded-xl data-[state=active]:bg-indigo-600 data-[state=active]:text-white data-[state=active]:shadow-lg transition-all font-bold text-xs uppercase tracking-widest"
                        >
                            <Camera className="w-4 h-4 mr-1.5" />
                            Scan
                        </TabsTrigger>
                        <TabsTrigger
                            value="claim"
                            className="flex-1 rounded-xl data-[state=active]:bg-indigo-600 data-[state=active]:text-white data-[state=active]:shadow-lg transition-all font-bold text-xs uppercase tracking-widest"
                        >
                            <Plus className="w-4 h-4 mr-1.5" />
                            Claim
                        </TabsTrigger>
                    </TabsList>

                    {/* Credentials Tab */}
                    <TabsContent value="wallet" className="space-y-4 outline-none">
                        <div className="flex items-center justify-between px-1">
                            <h3 className="text-xs font-black uppercase tracking-widest text-slate-400">Your Credentials</h3>
                            <span className="text-xs font-black text-indigo-600 bg-indigo-50 px-3 py-1.5 rounded-full border border-indigo-100">
                                {certs.length} {certs.length === 1 ? "Doc" : "Docs"}
                            </span>
                        </div>

                        <div className="space-y-3">
                            {loading ? (
                                <div className="py-16 text-center">
                                    <Loader2 className="w-8 h-8 text-indigo-600 animate-spin mx-auto mb-4" />
                                    <p className="text-slate-400 text-xs font-bold uppercase tracking-widest">Loading credentials...</p>
                                </div>
                            ) : certs.length > 0 ? (
                                certs.map((cert, index) => (
                                    <motion.div
                                        key={cert.id}
                                        initial={{ opacity: 0, y: 20 }}
                                        animate={{ opacity: 1, y: 0 }}
                                        transition={{ delay: index * 0.1 }}
                                        onClick={() => setSelectedCert(cert)}
                                        className="bg-white border border-slate-100 rounded-2xl p-4 shadow-lg shadow-slate-200/50 hover:shadow-xl active:scale-[0.98] transition-all cursor-pointer group"
                                    >
                                        <div className="flex items-center gap-4">
                                            <div className="w-12 h-12 bg-gradient-to-br from-indigo-500 to-violet-500 rounded-xl flex items-center justify-center shadow-lg shadow-indigo-600/20">
                                                <Award className="w-6 h-6 text-white" />
                                            </div>
                                            <div className="flex-1 min-w-0">
                                                <h4 className="font-bold text-slate-900 truncate">{cert.course_name}</h4>
                                                <p className="text-[10px] text-slate-400 font-bold uppercase tracking-widest">{cert.organization}</p>
                                            </div>
                                            <ChevronRight className="w-5 h-5 text-slate-300 group-hover:text-indigo-500 transition-colors" />
                                        </div>
                                    </motion.div>
                                ))
                            ) : (
                                <div className="py-16 text-center bg-white rounded-2xl border-2 border-dashed border-slate-200">
                                    <div className="w-16 h-16 bg-slate-50 rounded-2xl flex items-center justify-center mx-auto mb-4">
                                        <Award className="w-8 h-8 text-slate-200" />
                                    </div>
                                    <p className="text-slate-400 text-xs font-bold uppercase tracking-widest mb-4">No credentials yet</p>
                                    <Button
                                        onClick={() => setActiveTab("claim")}
                                        variant="outline"
                                        className="rounded-xl font-bold"
                                    >
                                        <Plus className="w-4 h-4 mr-2" />
                                        Claim Your First
                                    </Button>
                                </div>
                            )}
                        </div>
                    </TabsContent>

                    {/* QR Scanner Tab */}
                    <TabsContent value="scan" className="space-y-4 outline-none">
                        <div className="text-center mb-4">
                            <h3 className="text-lg font-black tracking-tight">Scan QR Code</h3>
                            <p className="text-slate-500 text-xs font-medium mt-1">
                                Point your camera at a credential QR code to verify it
                            </p>
                        </div>

                        <QRScanner
                            onScanSuccess={handleScanSuccess}
                            onScanError={(error) => setErrorMessage(error)}
                        />

                        {/* Verification Result */}
                        <AnimatePresence>
                            {verificationResult && (
                                <motion.div
                                    initial={{ opacity: 0, y: 20 }}
                                    animate={{ opacity: 1, y: 0 }}
                                    exit={{ opacity: 0, y: -20 }}
                                    className={`p-6 rounded-2xl border-2 ${
                                        verificationResult.summary?.all 
                                            ? "bg-emerald-50 border-emerald-200" 
                                            : "bg-red-50 border-red-200"
                                    }`}
                                >
                                    <div className="flex items-center gap-4 mb-4">
                                        <div className={`w-12 h-12 rounded-xl flex items-center justify-center ${
                                            verificationResult.summary?.all 
                                                ? "bg-emerald-500" 
                                                : "bg-red-500"
                                        }`}>
                                            {verificationResult.summary?.all ? (
                                                <ShieldCheck className="w-6 h-6 text-white" />
                                            ) : (
                                                <X className="w-6 h-6 text-white" />
                                            )}
                                        </div>
                                        <div>
                                            <h4 className={`font-bold ${
                                                verificationResult.summary?.all 
                                                    ? "text-emerald-700" 
                                                    : "text-red-700"
                                            }`}>
                                                {verificationResult.summary?.all ? "Verified!" : "Invalid"}
                                            </h4>
                                            <p className="text-xs text-slate-500">
                                                {verificationResult.certificate?.student_name} - {verificationResult.certificate?.course_name}
                                            </p>
                                        </div>
                                    </div>
                                    <Button
                                        onClick={() => setVerificationResult(null)}
                                        variant="outline"
                                        className="w-full rounded-xl"
                                    >
                                        Scan Another
                                    </Button>
                                </motion.div>
                            )}
                        </AnimatePresence>

                        {verifying && (
                            <div className="p-6 bg-white rounded-2xl border border-slate-200 text-center">
                                <Loader2 className="w-8 h-8 text-indigo-600 animate-spin mx-auto mb-3" />
                                <p className="text-slate-500 text-sm font-medium">Verifying credential...</p>
                            </div>
                        )}
                    </TabsContent>

                    {/* Claim Tab */}
                    <TabsContent value="claim" className="space-y-4 outline-none">
                        <Card className="border-0 shadow-xl shadow-slate-200/50 rounded-2xl bg-white overflow-hidden">
                            <div className="h-1.5 bg-gradient-to-r from-indigo-600 to-violet-600"></div>
                            <CardHeader className="text-center pb-2">
                                <CardTitle className="text-xl font-black tracking-tight">Claim Credential</CardTitle>
                                <CardDescription className="font-medium">Enter your 6-digit PIN from the issuer</CardDescription>
                            </CardHeader>
                            <CardContent className="space-y-5 pb-8">
                                <div className="space-y-2">
                                    <label className="text-[10px] font-black uppercase tracking-widest text-slate-400 ml-1">PIN Code</label>
                                    <input
                                        type="text"
                                        inputMode="numeric"
                                        placeholder="• • • • • •"
                                        value={claimPin}
                                        onChange={(e) => setClaimPin(e.target.value.replace(/\D/g, "").slice(0, 6))}
                                        className="w-full bg-slate-50 border border-slate-200 rounded-xl h-16 text-center text-2xl font-black tracking-[0.5em] focus:ring-4 focus:ring-indigo-600/10 focus:border-indigo-600 transition-all outline-none"
                                        maxLength={6}
                                    />
                                </div>

                                <div className="space-y-2">
                                    <label className="text-[10px] font-black uppercase tracking-widest text-slate-400 ml-1">Organization</label>
                                    <input
                                        type="text"
                                        value={organization}
                                        onChange={(e) => setOrganization(e.target.value)}
                                        className="w-full bg-slate-50 border border-slate-200 rounded-xl h-12 px-4 font-bold text-sm focus:ring-4 focus:ring-indigo-600/10 focus:border-indigo-600 transition-all outline-none"
                                    />
                                </div>

                                <Button
                                    onClick={handleClaim}
                                    disabled={claiming || claimPin.length < 6}
                                    className="w-full h-14 bg-gradient-to-r from-indigo-600 to-violet-600 hover:from-indigo-700 hover:to-violet-700 text-white font-black rounded-xl shadow-xl shadow-indigo-600/30 text-base transition-all active:scale-[0.98]"
                                >
                                    {claiming ? <Loader2 className="w-5 h-5 animate-spin" /> : "Claim Credential"}
                                </Button>
                            </CardContent>
                        </Card>

                        <div className="p-4 bg-amber-50 rounded-xl border border-amber-200">
                            <p className="text-xs text-amber-800 font-medium text-center">
                                Get your PIN from the institution that issued your credential
                            </p>
                        </div>
                    </TabsContent>
                </Tabs>
            </main>

            {/* Credential Detail Modal */}
            <AnimatePresence>
                {selectedCert && (
                    <motion.div
                        initial={{ opacity: 0 }}
                        animate={{ opacity: 1 }}
                        exit={{ opacity: 0 }}
                        className="fixed inset-0 z-[100] bg-slate-900/60 backdrop-blur-md flex items-end justify-center"
                        onClick={() => { setSelectedCert(null); setShowQRCode(false); }}
                    >
                        <motion.div
                            initial={{ y: "100%" }}
                            animate={{ y: 0 }}
                            exit={{ y: "100%" }}
                            transition={{ type: "spring", damping: 30, stiffness: 300 }}
                            className="w-full max-w-lg bg-white rounded-t-[2rem] p-6 pb-10 shadow-[0_-20px_60px_rgba(0,0,0,0.15)] mobile-safe-area"
                            onClick={(e) => e.stopPropagation()}
                        >
                            <div className="w-12 h-1.5 bg-slate-200 rounded-full mx-auto mb-6"></div>

                            {!showQRCode ? (
                                <>
                                    {/* Credential Info */}
                                    <div className="flex items-start justify-between mb-6">
                                        <div className="flex items-center gap-4">
                                            <div className="w-14 h-14 bg-gradient-to-br from-indigo-600 to-violet-600 rounded-2xl flex items-center justify-center text-white shadow-xl shadow-indigo-600/30">
                                                <Award className="w-7 h-7" />
                                            </div>
                                            <div>
                                                <h2 className="text-xl font-black text-slate-900 line-clamp-1">{selectedCert.course_name}</h2>
                                                <p className="text-xs font-bold text-slate-400 uppercase tracking-widest">{selectedCert.organization}</p>
                                            </div>
                                        </div>
                                        <button onClick={() => setSelectedCert(null)} className="p-2 hover:bg-slate-100 rounded-xl text-slate-400">
                                            <X className="w-5 h-5" />
                                        </button>
                                    </div>

                                    <div className="grid grid-cols-2 gap-3 mb-6">
                                        <div className="p-4 bg-slate-50 rounded-xl border border-slate-100">
                                            <p className="text-[10px] font-black text-slate-400 uppercase tracking-widest mb-1">Status</p>
                                            <div className="flex items-center gap-1.5 font-bold text-emerald-600 text-sm">
                                                <ShieldCheck className="w-4 h-4" />
                                                Verified
                                            </div>
                                        </div>
                                        <div className="p-4 bg-slate-50 rounded-xl border border-slate-100">
                                            <p className="text-[10px] font-black text-slate-400 uppercase tracking-widest mb-1">Issued</p>
                                            <p className="font-bold text-slate-700 text-sm">
                                                {new Date(selectedCert.issued_at).toLocaleDateString()}
                                            </p>
                                        </div>
                                    </div>

                                    {/* Action Buttons */}
                                    <div className="space-y-3">
                                        <Button
                                            onClick={() => generateQRCode(selectedCert.id)}
                                            className="w-full h-14 bg-gradient-to-r from-indigo-600 to-violet-600 hover:from-indigo-700 hover:to-violet-700 text-white font-black rounded-xl shadow-xl shadow-indigo-600/30"
                                        >
                                            <QrCode className="w-5 h-5 mr-2" />
                                            Show QR Code
                                        </Button>
                                        
                                        <div className="grid grid-cols-2 gap-3">
                                            <Button
                                                onClick={() => window.open(`${getApiBaseUrl()}/api/download/${selectedCert.id}`)}
                                                variant="outline"
                                                className="h-12 rounded-xl border-slate-200 font-bold"
                                            >
                                                <Download className="w-4 h-4 mr-2" />
                                                PDF
                                            </Button>
                                            <Button
                                                onClick={() => shareCredential(selectedCert)}
                                                variant="outline"
                                                className="h-12 rounded-xl border-slate-200 font-bold"
                                            >
                                                <Share2 className="w-4 h-4 mr-2" />
                                                Share
                                            </Button>
                                        </div>

                                        <Button
                                            onClick={() => window.open(`${window.location.origin}/verify-public?id=${selectedCert.id}`)}
                                            variant="ghost"
                                            className="w-full h-10 text-indigo-600 font-bold"
                                        >
                                            <ExternalLink className="w-4 h-4 mr-2" />
                                            Open Verification Page
                                        </Button>
                                    </div>
                                </>
                            ) : (
                                <>
                                    {/* QR Code Display */}
                                    <div className="text-center">
                                        <h3 className="text-lg font-black text-slate-900 mb-2">Scan to Verify</h3>
                                        <p className="text-xs text-slate-500 mb-6">Share this QR code to verify your credential</p>
                                        
                                        <div className="bg-white p-6 rounded-2xl shadow-xl inline-block mb-6 border border-slate-100">
                                            <img src={qrCodeData} alt="QR Code" className="w-56 h-56" />
                                        </div>

                                        <p className="text-[10px] text-slate-400 font-mono mb-6 break-all px-4">
                                            ID: {selectedCert.id}
                                        </p>

                                        <div className="space-y-3">
                                            <Button
                                                onClick={() => copyToClipboard(`${window.location.origin}/verify-public?id=${selectedCert.id}`)}
                                                variant="outline"
                                                className="w-full h-12 rounded-xl border-slate-200 font-bold"
                                            >
                                                <Copy className="w-4 h-4 mr-2" />
                                                Copy Verification Link
                                            </Button>
                                            <Button
                                                onClick={() => setShowQRCode(false)}
                                                variant="ghost"
                                                className="w-full h-10 text-slate-500 font-bold"
                                            >
                                                <ArrowLeft className="w-4 h-4 mr-2" />
                                                Back to Details
                                            </Button>
                                        </div>
                                    </div>
                                </>
                            )}
                        </motion.div>
                    </motion.div>
                )}
            </AnimatePresence>

            {/* Bottom Navigation */}
            <nav className="fixed bottom-0 inset-x-0 bg-white/95 backdrop-blur-xl border-t border-slate-200 z-50 mobile-safe-area">
                <div className="max-w-lg mx-auto px-6 h-20 flex items-center justify-around">
                    <button
                        onClick={() => setActiveTab("wallet")}
                        className={`flex flex-col items-center gap-1 py-2 px-4 rounded-xl transition-all ${
                            activeTab === "wallet" 
                                ? "text-indigo-600 bg-indigo-50" 
                                : "text-slate-400"
                        }`}
                    >
                        <Award className="w-6 h-6" />
                        <span className="text-[9px] font-black uppercase tracking-widest">Credentials</span>
                    </button>
                    
                    <button
                        onClick={() => setActiveTab("scan")}
                        className="relative -top-6"
                    >
                        <div className={`w-16 h-16 rounded-full flex items-center justify-center shadow-2xl border-4 border-white transition-all active:scale-95 ${
                            activeTab === "scan"
                                ? "bg-gradient-to-br from-indigo-600 to-violet-600 shadow-indigo-600/40"
                                : "bg-slate-800 shadow-slate-800/30"
                        }`}>
                            <Camera className="w-7 h-7 text-white" />
                        </div>
                    </button>
                    
                    <button
                        onClick={() => setActiveTab("claim")}
                        className={`flex flex-col items-center gap-1 py-2 px-4 rounded-xl transition-all ${
                            activeTab === "claim" 
                                ? "text-indigo-600 bg-indigo-50" 
                                : "text-slate-400"
                        }`}
                    >
                        <Plus className="w-6 h-6" />
                        <span className="text-[9px] font-black uppercase tracking-widest">Claim</span>
                    </button>
                </div>
            </nav>
        </div>
    )
}
