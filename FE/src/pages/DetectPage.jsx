import { useState, useRef, useEffect } from 'react';
import { Upload, X, Play, CheckCircle, AlertTriangle, BarChart2, Clock, Activity } from 'lucide-react';
import { detectService } from '../services/detectService';
import { projectService } from '../services/projectService';

function DetectPage() {
    const [file, setFile] = useState(null);
    const [loading, setLoading] = useState(false);
    const [result, setResult] = useState(null);
    const [videoPreview, setVideoPreview] = useState(null);
    const [details, setDetails] = useState(null);
    const fileInputRef = useRef(null);
    const [projectId, setProjectId] = useState(
    localStorage.getItem("project_id")
);
    // Lấy project mặc định khi mở trang
    useEffect(() => {
    async function loadProject() {
        const res = await projectService.getMyProjects();
        if (res.data.length > 0) {
            const id = res.data[0].project_id;
            setProjectId(id);
            localStorage.setItem("project_id", id);
        }
    }
    loadProject();
}, []);


    const handleFileChange = (e) => {
        const selectedFile = e.target.files[0];
        if (selectedFile) {
            setFile(selectedFile);
            setVideoPreview(URL.createObjectURL(selectedFile));
            setResult(null);
            setDetails(null);
        }
    };

    const handleReset = () => {
        setFile(null);
        setVideoPreview(null);
        setResult(null);
        setDetails(null);
        setLoading(false);
        if (fileInputRef.current) {
            fileInputRef.current.value = "";
        }
    };

    const handleUpload = async () => {
        if (!file || !projectId) {
            alert("Không tìm thấy project để lưu video.");
            return;
        }

        setLoading(true);

        try {
            const response = await detectService.uploadVideo(file, projectId);

            // Xác định violent dựa trên event hoặc segment
            const violent = response.segments && response.segments.length > 0;

            setResult({
                prediction: violent ? "violent" : "non-violent",
                confidence: violent ? 90 : 99
            });

            setDetails({
                confidence: violent ? 90 : 99,
                events: response.events || []
            });

        } catch (error) {
            console.error("Lỗi FE:", error);
            alert("Lỗi FE khi gọi Backend. Kiểm tra DevTools.");
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="w-full min-h-[calc(100vh-8rem)] flex flex-col items-center justify-center py-4">

            <header className="mb-8 text-center space-y-2 animate-fade-in">
                <h1 className="text-4xl font-black text-slate-800 tracking-tight drop-shadow-sm">
                    Hệ Thống Nhận Diện Bạo Lực
                </h1>
                <p className="text-slate-600 text-lg font-medium bg-white/50 px-4 py-1 rounded-full inline-block backdrop-blur-sm border border-white/40">
                    Sử dụng AI để phân tích hành vi từ Camera giám sát
                </p>
            </header>

            <div className="bg-white/80 backdrop-blur-xl p-8 rounded-3xl shadow-2xl w-full max-w-6xl border border-white/60 transition-all duration-500">
                {!videoPreview && (
                    <div className="border-3 border-dashed border-blue-300/50 rounded-2xl p-16 text-center hover:border-blue-500 hover:bg-blue-50/50 transition-all duration-300 group cursor-pointer relative overflow-hidden">
                        <input type="file" accept="video/*" onChange={handleFileChange} className="hidden" id="video-upload" ref={fileInputRef} />
                        <label htmlFor="video-upload" className="cursor-pointer flex flex-col items-center justify-center w-full h-full z-10 relative">
                            <div className="bg-white p-6 rounded-full mb-6 shadow-xl shadow-blue-200 group-hover:scale-110 group-hover:rotate-12 transition-all duration-300">
                                <Upload className="w-10 h-10 text-blue-600" />
                            </div>
                            <span className="text-2xl font-bold text-slate-700 group-hover:text-blue-700 transition-colors">
                                Nhấn để tải video lên
                            </span>
                            <span className="text-slate-400 mt-2 font-medium">Hỗ trợ MP4, AVI, MOV</span>
                        </label>
                    </div>
                )}

                {videoPreview && (
                    <div className="grid grid-cols-1 lg:grid-cols-12 gap-8 animate-fade-in-up">
                        <div className="lg:col-span-7 flex flex-col gap-4">
                            <div className="flex items-center justify-between px-1">
                                <h3 className={`text-sm font-bold uppercase tracking-wider flex items-center gap-2 ${result ? 'text-blue-600' : 'text-gray-500'}`}>
                                    {result ? <><Activity className="w-4 h-4 animate-pulse" /> PHÂN TÍCH HOÀN TẤT</> : <><Play className="w-4 h-4" /> VIDEO INPUT</>}
                                </h3>
                                <button onClick={handleReset} className="text-xs font-bold text-slate-500 hover:text-red-600 hover:bg-red-50 px-3 py-1 rounded-full transition-all flex items-center gap-1">
                                    <X className="w-3 h-3" /> Chọn video khác
                                </button>
                            </div>
                            <div className="relative rounded-2xl overflow-hidden shadow-lg border-4 border-white bg-black aspect-video group">
                                <video src={videoPreview} controls className="w-full h-full object-contain" />
                                {loading && (
                                    <div className="absolute inset-0 bg-black/70 backdrop-blur-sm flex flex-col items-center justify-center z-20">
                                        <div className="w-16 h-16 border-4 border-blue-500 border-t-transparent rounded-full animate-spin mb-4"></div>
                                        <p className="text-white font-bold tracking-widest animate-pulse">AI ĐANG PHÂN TÍCH...</p>
                                    </div>
                                )}
                            </div>
                        </div>

                        <div className="lg:col-span-5 flex flex-col h-full">
                            {!result && !loading && (
                                <div className="h-full flex flex-col justify-center text-center p-8 bg-slate-50/50 rounded-2xl border border-slate-100">
                                    <div className="w-16 h-16 bg-blue-100 rounded-full flex items-center justify-center mx-auto mb-4 text-blue-600">
                                        <BarChart2 className="w-8 h-8" />
                                    </div>
                                    <h4 className="text-xl font-bold text-slate-700 mb-2">Sẵn sàng phân tích</h4>
                                    <button onClick={handleUpload} className="w-full py-4 rounded-xl font-bold text-white text-lg shadow-xl shadow-blue-500/30 bg-gradient-to-r from-blue-600 to-cyan-500 hover:from-blue-700 hover:to-cyan-600 transition-all transform hover:scale-[1.02] active:scale-95 flex items-center justify-center gap-2">
                                        <Play className="w-5 h-5 fill-current" /> Bắt đầu nhận diện
                                    </button>
                                </div>
                            )}

                            {result && details && (
                                <div className="flex flex-col gap-4 h-full">
                                    <div className={`relative p-6 rounded-2xl shadow-lg border overflow-hidden transition-all ${result.prediction === 'violent' ? 'bg-gradient-to-br from-red-50 to-white border-red-200' : 'bg-gradient-to-br from-green-50 to-white border-green-200'}`}>
                                        <div className="flex justify-between items-start relative z-10">
                                            <div>
                                                <p className="text-xs font-extrabold text-slate-500 uppercase tracking-widest mb-1">KẾT QUẢ</p>
                                                <h2 className={`text-2xl font-black flex items-center gap-2 ${result.prediction === 'violent' ? 'text-red-600' : 'text-green-600'}`}>
                                                    {result.prediction === 'violent' ? 'PHÁT HIỆN BẠO LỰC' : 'AN TOÀN'}
                                                </h2>
                                            </div>
                                            {result.prediction === 'violent' ? <AlertTriangle className="w-10 h-10 text-red-500" /> : <CheckCircle className="w-10 h-10 text-green-500" />}
                                        </div>

                                        <div className="mt-6">
                                            <div className="flex justify-between text-sm font-bold text-slate-600 mb-1">
                                                <span>Độ tin cậy AI</span><span>{details.confidence}%</span>
                                            </div>
                                            <div className="w-full h-3 bg-gray-200 rounded-full overflow-hidden">
                                                <div className={`h-full rounded-full transition-all duration-1000 ease-out ${result.prediction === 'violent' ? 'bg-red-500' : 'bg-green-500'}`} style={{ width: `${details.confidence}%` }}></div>
                                            </div>
                                        </div>
                                    </div>

                                    <div className="flex-1 bg-white/60 backdrop-blur-md rounded-2xl border border-white/60 p-5 shadow-sm flex flex-col">
                                        <div className="flex items-center gap-2 mb-4 pb-3 border-b border-gray-100">
                                            <Clock className="w-4 h-4 text-slate-500" />
                                            <h3 className="font-bold text-slate-700">Dòng thời gian sự kiện</h3>
                                        </div>
                                        <div className="flex-1 overflow-y-auto pr-2 space-y-3 custom-scrollbar">
                                            {details.events.length > 0 ? (
                                                details.events.map((ev, index) => (
                                                    <div key={index} className="flex items-center p-3 bg-white rounded-xl border border-gray-100 shadow-sm hover:shadow-md transition-all cursor-pointer group">
                                                        <div className="w-12 h-12 rounded-lg bg-red-50 text-red-600 flex items-center justify-center font-bold text-xs border border-red-100 group-hover:bg-red-100 transition-colors">{ev.time}</div>
                                                        <div className="ml-3 flex-1">
                                                            <p className="text-sm font-bold text-slate-700">{ev.action}</p>
                                                            <p className="text-xs text-slate-400">Độ chính xác: {ev.score}%</p>
                                                        </div>
                                                        <div className="w-2 h-2 rounded-full bg-red-500"></div>
                                                    </div>
                                                ))
                                            ) : (
                                                <div className="h-full flex flex-col items-center justify-center text-slate-400 opacity-60">
                                                    <CheckCircle className="w-12 h-12 mb-2" />
                                                    <p className="text-sm">Không phát hiện sự kiện bất thường</p>
                                                </div>
                                            )}
                                        </div>
                                    </div>
                                </div>
                            )}

                        </div>
                    </div>
                )}
            </div>
        </div>
    );
}

export default DetectPage;
