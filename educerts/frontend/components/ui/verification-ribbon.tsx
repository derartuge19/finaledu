"use client"

import React, { useState } from "react"
import { motion, AnimatePresence } from "framer-motion"
import { ShieldCheck, CheckCircle, Calendar, User, Fingerprint, FileText, X, Info, Award } from "lucide-react"

interface SigningMetadata {
    signerName: string
    signerRole: string
    certificatesCount: number
    selectedCount: number
    hasSignature: boolean
    hasStamp: boolean
    signatureRecordId?: number
}

interface SigningRibbonProps {
    isSigningStep: boolean
    metadata?: SigningMetadata
    className?: string
}

export function SigningRibbon({ isSigningStep, metadata, className = "" }: SigningRibbonProps) {
    const [showDetails, setShowDetails] = useState(false)

    if (!isSigningStep) return null

    return (
        <>
            {/* Blue Ribbon */}
            <div 
                className={`fixed top-0 left-0 right-0 z-50 cursor-pointer ${className}`}
                onClick={() => setShowDetails(true)}
            >
                <div className="bg-gradient-to-r from-blue-600 to-blue-700 text-white px-6 py-3 shadow-lg">
                    <div className="max-w-7xl mx-auto flex items-center justify-between">
                        <div className="flex items-center gap-3">
                            <motion.div
                                initial={{ scale: 0 }}
                                animate={{ scale: 1 }}
                                transition={{ type: "spring", stiffness: 200, damping: 20 }}
                                className="w-8 h-8 bg-white/20 rounded-full flex items-center justify-center"
                            >
                                <Award className="w-5 h-5 text-white" />
                            </motion.div>
                            <div className="flex items-center gap-2">
                                <span className="font-bold text-lg">SIGNING MODE</span>
                                <CheckCircle className="w-5 h-5 text-green-300" />
                            </div>
                            <span className="text-blue-100 text-sm ml-4">
                                {metadata?.selectedCount || 0} of {metadata?.certificatesCount || 0} certificates selected
                            </span>
                        </div>
                        <div className="flex items-center gap-2 text-blue-100">
                            <Info className="w-4 h-4" />
                            <span className="text-sm font-medium">Click for signing details</span>
                        </div>
                    </div>
                </div>
                
                {/* Ribbon tail effect */}
                <div className="relative h-2">
                    <div className="absolute inset-0 bg-blue-700 transform skew-y-1"></div>
                </div>
            </div>

            {/* Metadata Popup */}
            <AnimatePresence>
                {showDetails && (
                    <>
                        {/* Backdrop */}
                        <motion.div
                            initial={{ opacity: 0 }}
                            animate={{ opacity: 1 }}
                            exit={{ opacity: 0 }}
                            className="fixed inset-0 bg-black/50 z-50 flex items-center justify-center p-4"
                            onClick={() => setShowDetails(false)}
                        >
                            {/* White Metadata Box */}
                            <motion.div
                                initial={{ opacity: 0, scale: 0.9, y: 20 }}
                                animate={{ opacity: 1, scale: 1, y: 0 }}
                                exit={{ opacity: 0, scale: 0.9, y: 20 }}
                                transition={{ type: "spring", stiffness: 300, damping: 30 }}
                                className="bg-white rounded-2xl shadow-2xl max-w-2xl w-full max-h-[80vh] overflow-hidden"
                                onClick={(e) => e.stopPropagation()}
                            >
                                {/* Header */}
                                <div className="bg-gradient-to-r from-blue-600 to-blue-700 text-white p-6">
                                    <div className="flex items-center justify-between">
                                        <div className="flex items-center gap-3">
                                            <div className="w-12 h-12 bg-white/20 rounded-full flex items-center justify-center">
                                                <Award className="w-7 h-7 text-white" />
                                            </div>
                                            <div>
                                                <h2 className="text-2xl font-bold">Verification Details</h2>
                                                <p className="text-blue-100">Certificate Authentication Information</p>
                                            </div>
                                        </div>
                                        <button
                                            onClick={() => setShowDetails(false)}
                                            className="w-8 h-8 bg-white/20 rounded-full flex items-center justify-center hover:bg-white/30 transition-colors"
                                        >
                                            <X className="w-5 h-5 text-white" />
                                        </button>
                                    </div>
                                </div>

                                {/* Content */}
                                <div className="p-6 space-y-6 max-h-[60vh] overflow-y-auto">
                                    {metadata && (
                                        <>
                                            {/* Signer Information */}
                                            <div className="space-y-4">
                                                <h3 className="text-lg font-semibold text-gray-900 flex items-center gap-2">
                                                    <User className="w-5 h-5 text-blue-600" />
                                                    Signer Information
                                                </h3>
                                                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                                                    <div className="bg-gray-50 rounded-xl p-4">
                                                        <div className="flex items-center gap-2 text-gray-600 text-sm font-medium mb-1">
                                                            <User className="w-4 h-4" />
                                                            Signer Name
                                                        </div>
                                                        <p className="font-semibold text-gray-900">{metadata.signerName}</p>
                                                    </div>
                                                    <div className="bg-gray-50 rounded-xl p-4">
                                                        <div className="flex items-center gap-2 text-gray-600 text-sm font-medium mb-1">
                                                            <Award className="w-4 h-4" />
                                                            Signer Role
                                                        </div>
                                                        <p className="font-semibold text-gray-900">{metadata.signerRole}</p>
                                                    </div>
                                                </div>
                                            </div>

                                            {/* Certificate Information */}
                                            <div className="space-y-4">
                                                <h3 className="text-lg font-semibold text-gray-900 flex items-center gap-2">
                                                    <FileText className="w-5 h-5 text-blue-600" />
                                                    Certificate Batch Information
                                                </h3>
                                                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                                                    <div className="bg-gray-50 rounded-xl p-4">
                                                        <div className="flex items-center justify-between mb-2">
                                                            <span className="text-sm font-medium text-gray-600">Total Certificates</span>
                                                            <span className="text-lg font-bold text-blue-600">{metadata.certificatesCount}</span>
                                                        </div>
                                                        <p className="text-xs text-gray-500">Certificates generated in this batch</p>
                                                    </div>
                                                    <div className="bg-gray-50 rounded-xl p-4">
                                                        <div className="flex items-center justify-between mb-2">
                                                            <span className="text-sm font-medium text-gray-600">Selected for Signing</span>
                                                            <span className="text-lg font-bold text-green-600">{metadata.selectedCount}</span>
                                                        </div>
                                                        <p className="text-xs text-gray-500">Certificates ready to be signed</p>
                                                    </div>
                                                </div>
                                            </div>

                                            {/* Signature Assets */}
                                            <div className="space-y-4">
                                                <h3 className="text-lg font-semibold text-gray-900 flex items-center gap-2">
                                                    <Fingerprint className="w-5 h-5 text-blue-600" />
                                                    Digital Signature Assets
                                                </h3>
                                                <div className="space-y-3">
                                                    <div className="bg-gray-50 rounded-xl p-4">
                                                        <div className="flex items-center justify-between mb-2">
                                                            <span className="text-sm font-medium text-gray-600">Signature Record ID</span>
                                                            <div className="flex items-center gap-1">
                                                                <CheckCircle className="w-4 h-4 text-green-500" />
                                                                <span className="text-xs text-green-600 font-medium">Active</span>
                                                            </div>
                                                        </div>
                                                        <p className="font-mono text-sm text-gray-900 bg-white px-3 py-2 rounded-lg border border-gray-200">
                                                            #{metadata.signatureRecordId || "N/A"}
                                                        </p>
                                                    </div>
                                                    
                                                    <div className="grid grid-cols-2 gap-4">
                                                        <div className={`${metadata.hasSignature ? "bg-green-50 border-green-200" : "bg-gray-50 border-gray-200"} border rounded-xl p-4`}>
                                                            <div className="flex items-center gap-2 mb-2">
                                                                <Award className={`w-5 h-5 ${metadata.hasSignature ? "text-green-600" : "text-gray-400"}`} />
                                                                <span className={`font-medium ${metadata.hasSignature ? "text-green-900" : "text-gray-600"}`}>Signature Image</span>
                                                            </div>
                                                            <p className={`text-sm ${metadata.hasSignature ? "text-green-700" : "text-gray-500"}`}>
                                                                {metadata.hasSignature ? "Uploaded & Ready" : "Not Uploaded"}
                                                            </p>
                                                        </div>
                                                        <div className={`${metadata.hasStamp ? "bg-green-50 border-green-200" : "bg-gray-50 border-gray-200"} border rounded-xl p-4`}>
                                                            <div className="flex items-center gap-2 mb-2">
                                                                <CheckCircle className={`w-5 h-5 ${metadata.hasStamp ? "text-green-600" : "text-gray-400"}`} />
                                                                <span className={`font-medium ${metadata.hasStamp ? "text-green-900" : "text-gray-600"}`}>Official Stamp</span>
                                                            </div>
                                                            <p className={`text-sm ${metadata.hasStamp ? "text-green-700" : "text-gray-500"}`}>
                                                                {metadata.hasStamp ? "Uploaded & Ready" : "Not Uploaded"}
                                                            </p>
                                                        </div>
                                                    </div>
                                                </div>
                                            </div>

                                            {/* Security Notice */}
                                            <div className="bg-blue-50 border border-blue-200 rounded-xl p-4">
                                                <div className="flex items-start gap-3">
                                                    <Info className="w-5 h-5 text-blue-600 mt-0.5" />
                                                    <div>
                                                        <h4 className="font-semibold text-blue-900 mb-1">Digital Signature Process</h4>
                                                        <p className="text-sm text-blue-700 leading-relaxed">
                                                            Your digital signature and official stamp will be cryptographically applied to each selected certificate. 
                                                            This process uses Ed25519 cryptographic signatures to ensure authenticity and tamper-proof verification.
                                                        </p>
                                                    </div>
                                                </div>
                                            </div>
                                        </>
                                    )}
                                </div>

                                {/* Footer */}
                                <div className="border-t border-gray-200 p-4 bg-gray-50">
                                    <button
                                        onClick={() => setShowDetails(false)}
                                        className="w-full bg-blue-600 hover:bg-blue-700 text-white font-semibold py-3 rounded-xl transition-colors"
                                    >
                                        Close
                                    </button>
                                </div>
                            </motion.div>
                        </motion.div>
                    </>
                )}
            </AnimatePresence>
        </>
    )
}
