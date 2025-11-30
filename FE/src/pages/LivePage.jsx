import { useState, useRef, useEffect } from 'react';
import { Camera, StopCircle, Activity, AlertTriangle, CheckCircle, Video } from 'lucide-react';

const LivePage = () => {
    const [isStreaming, setIsStreaming] = useState(false);
    const [status, setStatus] = useState("Đã ngắt kết nối");

    // Ref để thao tác với DOM
    const videoRef = useRef(null);      // Video gốc (ẩn đi, dùng để lấy hình)
    const canvasRef = useRef(null);     // Canvas để hiển thị kết quả từ Server về
    const wsRef = useRef(null);         // Lưu kết nối WebSocket
    const intervalRef = useRef(null);   // Lưu vòng lặp gửi ảnh

    // Hàm Bắt đầu Camera
    const startCamera = async () => {
        try {
            // 1. Xin quyền truy cập Webcam
            const stream = await navigator.mediaDevices.getUserMedia({
                video: { width: 640, height: 480 } // Giảm độ phân giải một chút để gửi cho nhanh
            });

            if (videoRef.current) {
                videoRef.current.srcObject = stream;
                videoRef.current.play(); // Chạy video gốc (nhưng mình sẽ ẩn nó đi)
            }

            // 2. Kết nối WebSocket tới Backend
            connectWebSocket();
            setIsStreaming(true);
            setStatus("Đang kết nối máy chủ...");

        } catch (err) {
            console.error("Lỗi camera:", err);
            alert("Không thể truy cập Camera! Vui lòng cấp quyền.");
        }
    };

    // Hàm Kết nối WebSocket
    const connectWebSocket = () => {
        // Lưu ý: Thay localhost bằng IP máy nếu test trên điện thoại
        const ws = new WebSocket("ws://127.0.0.1:8000/live/ws");
        wsRef.current = ws;

        ws.onopen = () => {
            console.log("Đã kết nối WebSocket");
            setStatus("Hệ thống đang chạy (Live)");

            // Bắt đầu gửi frame liên tục (20 FPS - tức là 50ms gửi 1 lần)
            intervalRef.current = setInterval(sendFrameToBackend, 50);
        };

        ws.onmessage = (event) => {
            // 4. Nhận ảnh đã vẽ Skeleton từ Backend và vẽ lên Canvas
            const imageSrc = event.data;
            const canvas = canvasRef.current;
            const ctx = canvas.getContext('2d');

            const img = new Image();
            img.onload = () => {
                canvas.width = img.width;
                canvas.height = img.height;
                ctx.drawImage(img, 0, 0); // Vẽ ảnh nhận được lên màn hình
            };
            img.src = imageSrc;
        };

        ws.onclose = () => setStatus("Mất kết nối máy chủ");
    };

    // Hàm gửi Frame đi
    const sendFrameToBackend = () => {
        if (!videoRef.current || !wsRef.current || wsRef.current.readyState !== WebSocket.OPEN) return;

        // Vẽ video hiện tại lên một canvas ẩn tạm thời để lấy dữ liệu ảnh
        const tempCanvas = document.createElement('canvas');
        tempCanvas.width = videoRef.current.videoWidth;
        tempCanvas.height = videoRef.current.videoHeight;
        const ctx = tempCanvas.getContext('2d');
        ctx.drawImage(videoRef.current, 0, 0);

        // Chuyển thành base64 và gửi đi
        const base64Data = tempCanvas.toDataURL('image/jpeg', 0.7); // Chất lượng 0.7 để nhẹ
        wsRef.current.send(base64Data);
    };

    // Hàm Tắt Camera
    const stopCamera = () => {
        // Dừng gửi ảnh
        if (intervalRef.current) clearInterval(intervalRef.current);

        // Đóng WebSocket
        if (wsRef.current) wsRef.current.close();

        // Tắt Webcam
        if (videoRef.current && videoRef.current.srcObject) {
            const tracks = videoRef.current.srcObject.getTracks();
            tracks.forEach(track => track.stop());
            videoRef.current.srcObject = null;
        }

        // Xóa canvas hiển thị
        const canvas = canvasRef.current;
        if (canvas) {
            const ctx = canvas.getContext('2d');
            ctx.clearRect(0, 0, canvas.width, canvas.height);
        }

        setIsStreaming(false);
        setStatus("Đã tắt Camera");
    };

    // Cleanup khi thoát trang
    useEffect(() => {
        return () => stopCamera();
    }, []);

    return (
        <div className="w-full min-h-[calc(100vh-8rem)] flex flex-col items-center justify-center py-4">

            <header className="mb-8 text-center space-y-2">
                <h1 className="text-3xl font-black text-slate-800 tracking-tight">Giám Sát Thời Gian Thực</h1>
                <p className="text-slate-600 bg-white/50 px-4 py-1 rounded-full inline-block backdrop-blur-sm border border-white/40">
                    Hệ thống phân tích hành vi Live-Stream (YOLOv8-Pose)
                </p>
            </header>

            <div className="bg-white/80 backdrop-blur-xl p-8 rounded-3xl shadow-2xl w-full max-w-5xl border border-white/60 relative">

                {/* Trạng thái */}
                <div className="absolute top-6 right-8 flex items-center gap-2">
                    <span className={`w-3 h-3 rounded-full ${isStreaming ? 'bg-green-500 animate-pulse' : 'bg-red-500'}`}></span>
                    <span className="text-sm font-bold text-slate-600 uppercase">{status}</span>
                </div>

                <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">

                    {/* Màn hình hiển thị chính (Canvas) */}
                    <div className="lg:col-span-2 bg-black rounded-2xl overflow-hidden shadow-inner border-4 border-white/50 relative aspect-video flex items-center justify-center">

                        {/* Video gốc (Ẩn đi, chỉ dùng để lấy source) */}
                        <video ref={videoRef} className="hidden" autoPlay playsInline muted />

                        {/* Canvas hiển thị kết quả từ Backend */}
                        <canvas ref={canvasRef} className="w-full h-full object-contain" />

                        {!isStreaming && (
                            <div className="absolute inset-0 flex flex-col items-center justify-center text-white/30">
                                <Video className="w-16 h-16 mb-2" />
                                <p className="font-bold">CAMERA OFF</p>
                            </div>
                        )}
                    </div>

                    {/* Bảng điều khiển bên phải */}
                    <div className="flex flex-col justify-center gap-4">
                        <div className="bg-white/50 p-4 rounded-xl border border-white/60">
                            <h3 className="font-bold text-slate-700 mb-2 flex items-center gap-2">
                                <Activity className="w-4 h-4 text-blue-600" /> Thông số Live
                            </h3>
                            <div className="space-y-2 text-sm text-slate-600">
                                <p className="flex justify-between"><span>Độ trễ (Latency):</span> <span className="font-mono font-bold">~50ms</span></p>
                                <p className="flex justify-between"><span>FPS Dự kiến:</span> <span className="font-mono font-bold">20 FPS</span></p>
                                <p className="flex justify-between"><span>Model:</span> <span className="font-mono font-bold">YOLOv8l-Pose</span></p>
                            </div>
                        </div>

                        {/* Nút điều khiển */}
                        {!isStreaming ? (
                            <button
                                onClick={startCamera}
                                className="w-full py-4 rounded-xl font-bold text-white text-lg shadow-lg bg-blue-600 hover:bg-blue-700 transition-all flex items-center justify-center gap-2"
                            >
                                <Camera className="w-6 h-6" /> BẬT CAMERA
                            </button>
                        ) : (
                            <button
                                onClick={stopCamera}
                                className="w-full py-4 rounded-xl font-bold text-white text-lg shadow-lg bg-red-500 hover:bg-red-600 transition-all flex items-center justify-center gap-2 animate-pulse"
                            >
                                <StopCircle className="w-6 h-6" /> TẮT CAMERA
                            </button>
                        )}

                        <div className="mt-4 p-4 bg-yellow-50 rounded-xl border border-yellow-100 text-xs text-yellow-800">
                            <p className="flex items-center gap-2 font-bold mb-1">
                                <AlertTriangle className="w-4 h-4" /> Lưu ý:
                            </p>
                            Hệ thống sẽ yêu cầu quyền truy cập Webcam. Dữ liệu hình ảnh sẽ được gửi lên server để xử lý và không được lưu lại.
                        </div>
                    </div>
                </div>
            </div>
        </div>
    );
};

export default LivePage;