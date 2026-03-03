"use client"

import React, { useState, useRef, useEffect } from "react"
import { useAuth } from "@/context/AuthContext"
import { motion } from "framer-motion"
import { Settings, User, Shield, Key, Bell, Globe, Cpu, Database, PenTool, Hash, Upload, Loader2, CheckCircle, X } from "lucide-react"
import { Card, CardContent, CardDescription, CardFooter, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import axios from "axios"
import { getApiBaseUrl } from "@/lib/api-config"

interface SignatureRecord {
    id: number
    signer_name: string
    signer_role: string
    has_signature: boolean
    has_stamp: boolean
    uploaded_at: string
}

export default function SettingsPage() {
    const { user } = useAuth()
    const [activeTab, setActiveTab] = useState("profile")
    const [signerName, setSignerName] = useState(user?.name || "")
    const [signerRole, setSignerRole] = useState("Authorized Signatory")
    const [signatureFile, setSignatureFile] = useState<File | null>(null)
    const [stampFile, setStampFile] = useState<File | null>(null)
    const [signaturePreview, setSignaturePreview] = useState<string | null>(null)
    const [stampPreview, setStampPreview] = useState<string | null>(null)
    const [uploading, setUploading] = useState(false)
    const [uploadSuccess, setUploadSuccess] = useState(false)
    const [records, setRecords] = useState<SignatureRecord[]>([])
    const [loadingRecords, setLoadingRecords] = useState(true)
    
    const signatureInputRef = useRef<HTMLInputElement>(null)
    const stampInputRef = useRef<HTMLInputElement>(null)

    // Fetch existing signature records
    useEffect(() => {
        fetchSignatureRecords()
    }, [])

    const fetchSignatureRecords = async () => {
        try {
            const res = await axios.get(`${getApiBaseUrl()}/api/sign/records`, {
                withCredentials: true
            })
            setRecords(res.data)
        } catch (error) {
            console.error("Failed to fetch signature records", error)
        } finally {
            setLoadingRecords(false)
        }
    }

    const handleSignatureSelect = (e: React.ChangeEvent<HTMLInputElement>) => {
        const file = e.target.files?.[0]
        if (file) {
            setSignatureFile(file)
            const reader = new FileReader()
            reader.onloadend = () => setSignaturePreview(reader.result as string)
            reader.readAsDataURL(file)
        }
    }

    const handleStampSelect = (e: React.ChangeEvent<HTMLInputElement>) => {
        const file = e.target.files?.[0]
        if (file) {
            setStampFile(file)
            const reader = new FileReader()
            reader.onloadend = () => setStampPreview(reader.result as string)
            reader.readAsDataURL(file)
        }
    }

    const handleUpload = async () => {
        if (!signatureFile && !stampFile) return
        
        setUploading(true)
        setUploadSuccess(false)
        
        try {
            const formData = new FormData()
            if (signatureFile) formData.append("signature_file", signatureFile)
            if (stampFile) formData.append("stamp_file", stampFile)
            formData.append("signer_name", signerName)
            formData.append("signer_role", signerRole)
            
            await axios.post(`${getApiBaseUrl()}/api/sign/upload`, formData, {
                headers: { "Content-Type": "multipart/form-data" },
                withCredentials: true
            })
            
            setUploadSuccess(true)
            setSignatureFile(null)
            setStampFile(null)
            setSignaturePreview(null)
            setStampPreview(null)
            fetchSignatureRecords()
            
            setTimeout(() => setUploadSuccess(false), 3000)
        } catch (error) {
            console.error("Upload failed", error)
            alert("Failed to upload signature assets")
        } finally {
            setUploading(false)
        }
    }

    return (
        <div className="p-8 max-w-4xl mx-auto space-y-8">
            <div className="flex items-center gap-3">
                <Settings className="w-8 h-8 text-indigo-600" />
                <h1 className="text-3xl font-bold text-slate-900 tracking-tight">System Settings</h1>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
                {/* Sidebar Nav (Internal) */}
                <div className="space-y-1">
                    {[
                        { name: "My Profile", icon: User, id: "profile" },
                        { name: "Security", icon: Shield, id: "security" },
                        { name: "API Keys", icon: Key, id: "api-keys" },
                        { name: "Signatures", icon: PenTool, id: "signatures" },
                        { name: "Notifications", icon: Bell, id: "notifications" },
                        { name: "Integration", icon: Globe, id: "integration" },
                    ].map((item) => (
                        <button
                            key={item.name}
                            onClick={() => setActiveTab(item.id)}
                            className={`w-full flex items-center gap-3 px-4 py-2.5 rounded-xl text-sm font-bold transition-all ${activeTab === item.id ? "bg-white text-indigo-600 border border-slate-200 shadow-sm" : "text-slate-500 hover:text-slate-900 hover:bg-slate-50"}`}
                        >
                            <item.icon className={`w-4 h-4 ${activeTab === item.id ? "text-indigo-600" : "text-slate-400"}`} />
                            {item.name}
                        </button>
                    ))}
                </div>

                {/* Main Content */}
                <div className="md:col-span-2 space-y-6">
                    {/* Profile Tab */}
                    {activeTab === "profile" && (
                        <Card className="bg-white border-slate-200 shadow-sm rounded-2xl">
                            <CardHeader>
                                <CardTitle className="text-lg text-slate-900">Profile Information</CardTitle>
                                <CardDescription className="font-medium">Update your personal details and account settings.</CardDescription>
                            </CardHeader>
                            <CardContent className="space-y-4">
                                <div className="flex items-center gap-4 p-4 rounded-xl bg-slate-50 border border-slate-100 shadow-inner">
                                    <div className="w-16 h-16 rounded-full bg-indigo-600 flex items-center justify-center text-xl font-bold text-white shadow-lg shadow-indigo-600/20">
                                        {user?.name?.[0].toUpperCase()}
                                    </div>
                                    <div>
                                        <h4 className="font-bold text-slate-900 text-lg">{user?.name}</h4>
                                        <p className="text-sm text-slate-500 font-medium">{user?.email}</p>
                                        <span className={`inline-block mt-2 px-2 py-0.5 rounded text-[10px] font-bold uppercase tracking-widest ${user?.is_admin ? "bg-indigo-100 text-indigo-600 border border-indigo-200 text-indigo-700" : "bg-slate-200 text-slate-600"}`}>
                                            {user?.is_admin ? "Administrator" : "Verified Student"}
                                        </span>
                                    </div>
                                    <Button variant="outline" size="sm" className="ml-auto bg-white border-slate-200 shadow-sm font-bold">Edit</Button>
                                </div>
                            </CardContent>
                        </Card>
                    )}

                    {/* Security Tab */}
                    {activeTab === "security" && (
                        <Card className="bg-white border-slate-200 shadow-sm rounded-2xl">
                            <CardHeader>
                                <CardTitle className="text-lg text-slate-900">Security & Encryption</CardTitle>
                                <CardDescription className="font-medium text-slate-500">Your account is protected by industry-standard cryptography.</CardDescription>
                            </CardHeader>
                            <CardContent className="space-y-4">
                                <div className="space-y-4">
                                    <div className="flex items-start gap-4">
                                        <div className="p-2 bg-indigo-50 rounded-lg border border-indigo-100">
                                            <Cpu className="w-5 h-5 text-indigo-600" />
                                        </div>
                                        <div>
                                            <h5 className="text-sm font-bold text-slate-900">Asymmetric Signing (Ed25519)</h5>
                                            <p className="text-xs text-slate-500 mt-1 font-medium">Every credential issued is signed using a unique Ed25519 private key. The public key is embedded in the JSON for verification.</p>
                                        </div>
                                    </div>
                                    <div className="flex items-start gap-4">
                                        <div className="p-2 bg-indigo-50 rounded-lg border border-indigo-100">
                                            <Database className="w-5 h-5 text-indigo-600" />
                                        </div>
                                        <div>
                                            <h5 className="text-sm font-bold text-slate-900">Field Salting (OpenAttestation v2)</h5>
                                            <p className="text-xs text-slate-500 mt-1 font-medium">Individual fields are salted to prevent brute-force dictionary attacks on certificate data. Selective disclosure ready.</p>
                                        </div>
                                    </div>
                                    <div className="flex items-start gap-4">
                                        <div className="p-2 bg-indigo-50 rounded-lg border border-indigo-100">
                                            <Shield className="w-5 h-5 text-indigo-600" />
                                        </div>
                                        <div>
                                            <h5 className="text-sm font-bold text-slate-900">Content Hash Verification</h5>
                                            <p className="text-xs text-slate-500 mt-1 font-medium">SHA-256 hashes are computed for all PDFs to detect tampering. Any modification to certificate content will fail verification.</p>
                                        </div>
                                    </div>
                                </div>
                            </CardContent>
                            <CardFooter className="pt-0">
                                <Button variant="link" className="text-indigo-600 text-xs p-0 font-bold">Learn more about our security model</Button>
                            </CardFooter>
                        </Card>
                    )}

                    {/* Signatures Tab */}
                    {activeTab === "signatures" && (
                        <Card id="signatures" className="bg-white border-indigo-200 shadow-lg shadow-indigo-500/5 rounded-2xl overflow-hidden ring-1 ring-indigo-50">
                            <div className="h-1.5 bg-indigo-600 w-full"></div>
                            <CardHeader>
                                <CardTitle className="text-lg text-slate-900 flex items-center gap-2">
                                    <PenTool className="w-5 h-5 text-indigo-600" />
                                    Authorized Signatures
                                </CardTitle>
                                <CardDescription className="font-medium text-slate-500">Manage your digital stamp and signature profile for certificate sealing.</CardDescription>
                            </CardHeader>
                            <CardContent className="space-y-6">
                                {/* Signer Info */}
                                <div className="grid grid-cols-2 gap-4">
                                    <div className="space-y-2">
                                        <label className="text-xs font-bold text-slate-500 uppercase tracking-wider">Signer Name</label>
                                        <input
                                            type="text"
                                            value={signerName}
                                            onChange={(e) => setSignerName(e.target.value)}
                                            className="w-full px-4 py-2 rounded-xl border border-slate-200 focus:ring-2 focus:ring-indigo-600/20 focus:border-indigo-600 outline-none text-sm font-semibold"
                                            placeholder="Enter signer name"
                                        />
                                    </div>
                                    <div className="space-y-2">
                                        <label className="text-xs font-bold text-slate-500 uppercase tracking-wider">Signer Role</label>
                                        <input
                                            type="text"
                                            value={signerRole}
                                            onChange={(e) => setSignerRole(e.target.value)}
                                            className="w-full px-4 py-2 rounded-xl border border-slate-200 focus:ring-2 focus:ring-indigo-600/20 focus:border-indigo-600 outline-none text-sm font-semibold"
                                            placeholder="e.g. Principal, Dean"
                                        />
                                    </div>
                                </div>

                                {/* Upload Areas */}
                                <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                                    {/* Signature Upload */}
                                    <div 
                                        onClick={() => signatureInputRef.current?.click()}
                                        className="p-6 rounded-2xl border-2 border-dashed border-slate-200 hover:border-indigo-400 transition-colors bg-slate-50 flex flex-col items-center justify-center text-center group cursor-pointer relative overflow-hidden min-h-[160px]"
                                    >
                                        <input
                                            ref={signatureInputRef}
                                            type="file"
                                            accept="image/png,image/jpeg,image/jpg"
                                            className="hidden"
                                            onChange={handleSignatureSelect}
                                        />
                                        {signaturePreview ? (
                                            <div className="relative w-full">
                                                <img src={signaturePreview} alt="Signature preview" className="max-h-24 mx-auto object-contain" />
                                                <button 
                                                    onClick={(e) => { e.stopPropagation(); setSignatureFile(null); setSignaturePreview(null); }}
                                                    className="absolute -top-2 -right-2 w-6 h-6 bg-red-500 text-white rounded-full flex items-center justify-center hover:bg-red-600"
                                                >
                                                    <X className="w-3 h-3" />
                                                </button>
                                            </div>
                                        ) : (
                                            <>
                                                <div className="w-12 h-12 rounded-full bg-white shadow-sm flex items-center justify-center mb-3 group-hover:scale-110 transition-transform">
                                                    <PenTool className="w-6 h-6 text-slate-400 group-hover:text-indigo-600" />
                                                </div>
                                                <p className="text-xs font-black text-slate-600 uppercase tracking-widest">Digital Signature</p>
                                                <p className="text-[10px] text-slate-400 mt-1 font-bold">Click to upload PNG</p>
                                            </>
                                        )}
                                    </div>

                                    {/* Stamp Upload */}
                                    <div 
                                        onClick={() => stampInputRef.current?.click()}
                                        className="p-6 rounded-2xl border-2 border-dashed border-slate-200 hover:border-indigo-400 transition-colors bg-slate-50 flex flex-col items-center justify-center text-center group cursor-pointer relative overflow-hidden min-h-[160px]"
                                    >
                                        <input
                                            ref={stampInputRef}
                                            type="file"
                                            accept="image/png,image/jpeg,image/jpg"
                                            className="hidden"
                                            onChange={handleStampSelect}
                                        />
                                        {stampPreview ? (
                                            <div className="relative w-full">
                                                <img src={stampPreview} alt="Stamp preview" className="max-h-24 mx-auto object-contain" />
                                                <button 
                                                    onClick={(e) => { e.stopPropagation(); setStampFile(null); setStampPreview(null); }}
                                                    className="absolute -top-2 -right-2 w-6 h-6 bg-red-500 text-white rounded-full flex items-center justify-center hover:bg-red-600"
                                                >
                                                    <X className="w-3 h-3" />
                                                </button>
                                            </div>
                                        ) : (
                                            <>
                                                <div className="w-12 h-12 rounded-full bg-white shadow-sm flex items-center justify-center mb-3 group-hover:scale-110 transition-transform">
                                                    <Hash className="w-6 h-6 text-slate-400 group-hover:text-indigo-600" />
                                                </div>
                                                <p className="text-xs font-black text-slate-600 uppercase tracking-widest">Official Stamp</p>
                                                <p className="text-[10px] text-slate-400 mt-1 font-bold">Click to upload seal</p>
                                            </>
                                        )}
                                    </div>
                                </div>

                                {/* Upload Button */}
                                <Button 
                                    onClick={handleUpload}
                                    disabled={uploading || (!signatureFile && !stampFile) || !signerName}
                                    className="w-full h-12 bg-indigo-600 hover:bg-indigo-700 text-white font-bold rounded-xl shadow-lg shadow-indigo-600/20"
                                >
                                    {uploading ? (
                                        <><Loader2 className="w-5 h-5 animate-spin mr-2" /> Uploading...</>
                                    ) : uploadSuccess ? (
                                        <><CheckCircle className="w-5 h-5 mr-2" /> Upload Successful!</>
                                    ) : (
                                        <><Upload className="w-5 h-5 mr-2" /> Upload Signature Assets</>
                                    )}
                                </Button>

                                {/* Previous Records */}
                                {records.length > 0 && (
                                    <div className="space-y-3 pt-4 border-t border-slate-100">
                                        <p className="text-xs font-bold text-slate-500 uppercase tracking-wider">Previous Signatures</p>
                                        <div className="space-y-2 max-h-40 overflow-y-auto">
                                            {records.map((record) => (
                                                <div key={record.id} className="flex items-center justify-between p-3 bg-slate-50 rounded-xl border border-slate-100">
                                                    <div>
                                                        <p className="text-sm font-semibold text-slate-900">{record.signer_name}</p>
                                                        <p className="text-xs text-slate-500">{record.signer_role}</p>
                                                    </div>
                                                    <div className="flex gap-2">
                                                        {record.has_signature && (
                                                            <span className="px-2 py-1 bg-indigo-100 text-indigo-600 text-[10px] font-bold rounded uppercase">Sig</span>
                                                        )}
                                                        {record.has_stamp && (
                                                            <span className="px-2 py-1 bg-emerald-100 text-emerald-600 text-[10px] font-bold rounded uppercase">Stamp</span>
                                                        )}
                                                    </div>
                                                </div>
                                            ))}
                                        </div>
                                    </div>
                                )}

                                <div className="p-4 rounded-xl bg-amber-50 border border-amber-100 flex gap-3 items-start">
                                    <Shield className="w-5 h-5 text-amber-600 mt-0.5" />
                                    <div className="text-xs text-amber-800 font-medium leading-relaxed">
                                        <p className="font-bold">Security Note:</p>
                                        These assets are only used to visually represent your cryptographic signature on the final PDF documents. They are stored securely and never shared publicly.
                                    </div>
                                </div>
                            </CardContent>
                        </Card>
                    )}

                    {/* API Keys Tab */}
                    {activeTab === "api-keys" && (
                        <Card className="bg-white border-slate-200 shadow-sm rounded-2xl">
                            <CardHeader>
                                <CardTitle className="text-lg text-slate-900 flex items-center gap-2">
                                    <Key className="w-5 h-5 text-indigo-600" />
                                    API Keys
                                </CardTitle>
                                <CardDescription className="font-medium text-slate-500">Manage API keys for programmatic access to EduCerts.</CardDescription>
                            </CardHeader>
                            <CardContent className="space-y-4">
                                <div className="p-4 rounded-xl bg-slate-50 border border-slate-100">
                                    <p className="text-sm text-slate-600 font-medium">API keys are not yet implemented. This feature will allow you to:</p>
                                    <ul className="mt-2 text-xs text-slate-500 space-y-1 ml-4">
                                        <li>• Issue certificates programmatically</li>
                                        <li>• Verify certificates via API</li>
                                        <li>• Access certificate data</li>
                                        <li>• Manage bulk operations</li>
                                    </ul>
                                </div>
                            </CardContent>
                        </Card>
                    )}

                    {/* Notifications Tab */}
                    {activeTab === "notifications" && (
                        <Card className="bg-white border-slate-200 shadow-sm rounded-2xl">
                            <CardHeader>
                                <CardTitle className="text-lg text-slate-900 flex items-center gap-2">
                                    <Bell className="w-5 h-5 text-indigo-600" />
                                    Notifications
                                </CardTitle>
                                <CardDescription className="font-medium text-slate-500">Configure notification preferences and alerts.</CardDescription>
                            </CardHeader>
                            <CardContent className="space-y-4">
                                <div className="p-4 rounded-xl bg-slate-50 border border-slate-100">
                                    <p className="text-sm text-slate-600 font-medium">Notification settings are not yet implemented. Future features will include:</p>
                                    <ul className="mt-2 text-xs text-slate-500 space-y-1 ml-4">
                                        <li>• Email notifications for certificate issuance</li>
                                        <li>• Alerts for verification attempts</li>
                                        <li>• Security notifications</li>
                                        <li>• System status updates</li>
                                    </ul>
                                </div>
                            </CardContent>
                        </Card>
                    )}

                    {/* Integration Tab */}
                    {activeTab === "integration" && (
                        <Card className="bg-white border-slate-200 shadow-sm rounded-2xl">
                            <CardHeader>
                                <CardTitle className="text-lg text-slate-900 flex items-center gap-2">
                                    <Globe className="w-5 h-5 text-indigo-600" />
                                    Integration
                                </CardTitle>
                                <CardDescription className="font-medium text-slate-500">Connect EduCerts with external systems and services.</CardDescription>
                            </CardHeader>
                            <CardContent className="space-y-4">
                                <div className="p-4 rounded-xl bg-slate-50 border border-slate-100">
                                    <p className="text-sm text-slate-600 font-medium">Integration options are not yet implemented. Future integrations will include:</p>
                                    <ul className="mt-2 text-xs text-slate-500 space-y-1 ml-4">
                                        <li>• Student Information Systems (SIS)</li>
                                        <li>• Learning Management Systems (LMS)</li>
                                        <li>• Blockchain networks</li>
                                        <li>• Third-party verification services</li>
                                    </ul>
                                </div>
                            </CardContent>
                        </Card>
                    )}

                    <div className="flex justify-end gap-3">
                        <Button variant="ghost" className="text-slate-400 font-bold">Cancel</Button>
                        <Button className="bg-indigo-600 hover:bg-indigo-700 text-white shadow-lg shadow-indigo-600/20 font-bold">Save Changes</Button>
                    </div>
                </div>
            </div>
        </div>
    )
}
