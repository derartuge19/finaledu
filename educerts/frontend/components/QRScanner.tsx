"use client"

import React, { useEffect, useRef, useState } from "react"
import { Html5Qrcode, Html5QrcodeScanner } from "html5-qrcode"
import { Camera, CameraOff, RefreshCw, Flashlight, X } from "lucide-react"
import { Button } from "@/components/ui/button"

interface QRScannerProps {
    onScanSuccess: (decodedText: string) => void
    onScanError?: (error: string) => void
    onClose?: () => void
}

export default function QRScanner({ onScanSuccess, onScanError, onClose }: QRScannerProps) {
    const [isScanning, setIsScanning] = useState(false)
    const [hasPermission, setHasPermission] = useState<boolean | null>(null)
    const [error, setError] = useState<string | null>(null)
    const [cameras, setCameras] = useState<{ id: string; label: string }[]>([])
    const [selectedCamera, setSelectedCamera] = useState<string>("")
    const scannerRef = useRef<Html5Qrcode | null>(null)
    const containerRef = useRef<HTMLDivElement>(null)

    useEffect(() => {
        // Get available cameras
        Html5Qrcode.getCameras()
            .then((devices) => {
                if (devices && devices.length > 0) {
                    setCameras(devices)
                    // Prefer back camera on mobile
                    const backCamera = devices.find(
                        (d) => d.label.toLowerCase().includes("back") || d.label.toLowerCase().includes("rear")
                    )
                    setSelectedCamera(backCamera?.id || devices[0].id)
                    setHasPermission(true)
                } else {
                    setError("No cameras found on this device")
                    setHasPermission(false)
                }
            })
            .catch((err) => {
                console.error("Camera permission error:", err)
                setError("Camera access denied. Please allow camera permissions.")
                setHasPermission(false)
            })

        return () => {
            stopScanning()
        }
    }, [])

    const startScanning = async () => {
        if (!selectedCamera) return

        try {
            setError(null)
            setIsScanning(true)

            if (scannerRef.current) {
                await scannerRef.current.stop()
            }

            scannerRef.current = new Html5Qrcode("qr-reader")

            await scannerRef.current.start(
                selectedCamera,
                {
                    fps: 10,
                    qrbox: { width: 250, height: 250 },
                    aspectRatio: 1.0,
                },
                (decodedText) => {
                    // Success callback
                    onScanSuccess(decodedText)
                    stopScanning()
                },
                (errorMessage) => {
                    // Error callback (ignore continuous scanning errors)
                }
            )
        } catch (err: any) {
            console.error("Scanner start error:", err)
            setError(err.message || "Failed to start camera")
            setIsScanning(false)
            if (onScanError) onScanError(err.message)
        }
    }

    const stopScanning = async () => {
        try {
            if (scannerRef.current && scannerRef.current.isScanning) {
                await scannerRef.current.stop()
            }
        } catch (err) {
            console.error("Stop scanning error:", err)
        }
        setIsScanning(false)
    }

    const switchCamera = () => {
        if (cameras.length <= 1) return
        const currentIndex = cameras.findIndex((c) => c.id === selectedCamera)
        const nextIndex = (currentIndex + 1) % cameras.length
        setSelectedCamera(cameras[nextIndex].id)
        if (isScanning) {
            stopScanning().then(() => {
                setTimeout(() => startScanning(), 500)
            })
        }
    }

    return (
        <div className="relative w-full">
            {/* Close Button */}
            {onClose && (
                <button
                    onClick={() => {
                        stopScanning()
                        onClose()
                    }}
                    className="absolute -top-2 -right-2 z-20 w-10 h-10 bg-slate-900 text-white rounded-full flex items-center justify-center shadow-xl hover:bg-slate-800 transition-colors"
                >
                    <X className="w-5 h-5" />
                </button>
            )}

            {/* Scanner Container */}
            <div className="relative overflow-hidden rounded-[2rem] bg-slate-900">
                {/* QR Reader Element */}
                <div
                    id="qr-reader"
                    ref={containerRef}
                    className="w-full aspect-square bg-slate-900"
                />

                {/* Scanner Overlay */}
                {isScanning && (
                    <div className="absolute inset-0 pointer-events-none">
                        {/* Corner Markers */}
                        <div className="absolute inset-0 flex items-center justify-center">
                            <div className="w-64 h-64 relative">
                                {/* Top Left */}
                                <div className="absolute top-0 left-0 w-12 h-12 border-t-4 border-l-4 border-indigo-500 rounded-tl-lg" />
                                {/* Top Right */}
                                <div className="absolute top-0 right-0 w-12 h-12 border-t-4 border-r-4 border-indigo-500 rounded-tr-lg" />
                                {/* Bottom Left */}
                                <div className="absolute bottom-0 left-0 w-12 h-12 border-b-4 border-l-4 border-indigo-500 rounded-bl-lg" />
                                {/* Bottom Right */}
                                <div className="absolute bottom-0 right-0 w-12 h-12 border-b-4 border-r-4 border-indigo-500 rounded-br-lg" />
                                {/* Scanning Line Animation */}
                                <div className="absolute left-4 right-4 h-0.5 bg-indigo-500 animate-scan-line" />
                            </div>
                        </div>
                    </div>
                )}

                {/* Not Scanning State */}
                {!isScanning && (
                    <div className="absolute inset-0 flex flex-col items-center justify-center bg-slate-900/95">
                        <div className="w-20 h-20 bg-slate-800 rounded-2xl flex items-center justify-center mb-4">
                            {hasPermission === false ? (
                                <CameraOff className="w-10 h-10 text-red-400" />
                            ) : (
                                <Camera className="w-10 h-10 text-slate-400" />
                            )}
                        </div>
                        <p className="text-slate-400 text-sm font-medium text-center px-8">
                            {hasPermission === null
                                ? "Requesting camera access..."
                                : hasPermission === false
                                ? error || "Camera access denied"
                                : "Tap the button below to start scanning"}
                        </p>
                    </div>
                )}
            </div>

            {/* Error Display */}
            {error && (
                <div className="mt-4 p-4 bg-red-50 border border-red-200 rounded-2xl">
                    <p className="text-red-600 text-sm font-medium text-center">{error}</p>
                </div>
            )}

            {/* Controls */}
            <div className="mt-6 flex gap-3">
                {!isScanning ? (
                    <Button
                        onClick={startScanning}
                        disabled={!hasPermission || !selectedCamera}
                        className="flex-1 h-14 bg-indigo-600 hover:bg-indigo-700 text-white font-bold rounded-2xl shadow-xl shadow-indigo-600/20"
                    >
                        <Camera className="w-5 h-5 mr-2" />
                        Start Camera
                    </Button>
                ) : (
                    <Button
                        onClick={stopScanning}
                        variant="outline"
                        className="flex-1 h-14 border-slate-200 text-slate-600 font-bold rounded-2xl"
                    >
                        <CameraOff className="w-5 h-5 mr-2" />
                        Stop Camera
                    </Button>
                )}

                {cameras.length > 1 && (
                    <Button
                        onClick={switchCamera}
                        variant="outline"
                        className="h-14 px-4 border-slate-200 text-slate-600 rounded-2xl"
                    >
                        <RefreshCw className="w-5 h-5" />
                    </Button>
                )}
            </div>

            {/* Camera Selector */}
            {cameras.length > 1 && (
                <div className="mt-4">
                    <p className="text-[10px] font-bold text-slate-400 uppercase tracking-widest mb-2">Select Camera</p>
                    <select
                        value={selectedCamera}
                        onChange={(e) => setSelectedCamera(e.target.value)}
                        className="w-full p-3 bg-slate-50 border border-slate-200 rounded-xl text-sm font-medium focus:ring-2 focus:ring-indigo-600/20 outline-none"
                    >
                        {cameras.map((camera) => (
                            <option key={camera.id} value={camera.id}>
                                {camera.label || `Camera ${camera.id}`}
                            </option>
                        ))}
                    </select>
                </div>
            )}

            {/* Scanning Instructions */}
            <div className="mt-6 p-4 bg-indigo-50 rounded-2xl border border-indigo-100">
                <p className="text-xs text-indigo-800 font-medium text-center leading-relaxed">
                    Position the QR code within the frame. The scanner will automatically detect and verify the credential.
                </p>
            </div>
        </div>
    )
}
