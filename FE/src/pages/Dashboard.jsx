import { useState, useEffect } from 'react';
import { dashboardService } from '../services/dashboardService';
import toast from 'react-hot-toast';
import {
    BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer
} from 'recharts';
import {
    Video, AlertTriangle, CheckCircle, HardDrive, Activity,
    Clock, Trash2, AlertOctagon
} from 'lucide-react';

const Dashboard = () => {
    // State dữ liệu
    const [stats, setStats] = useState({
        total_videos: 0,
        total_violence: 0,
        avg_confidence: 0,
        recent_activities: [],
        chart_data: []
    });

    // State Refresh Key (Chìa khóa để làm mới dữ liệu)
    const [refreshKey, setRefreshKey] = useState(0);

    // State Modal Xóa
    const [showModal, setShowModal] = useState(false);
    const [deleteId, setDeleteId] = useState(null);

    // --- SỬA LỖI Ở ĐÂY: Đưa hàm fetch vào trong useEffect ---
    useEffect(() => {
        const loadData = async () => {
            try {
                // CŨ: const res = await axios.get("http://127.0.0.1:8000/dashboard/stats");
                // MỚI: Gọn gàng hơn nhiều
                const res = await dashboardService.getStats();
                setStats(res.data);
            } catch (error) {
                console.error("Lỗi tải dữ liệu:", error);
            }
        };

        // 1. Gọi ngay lập tức khi vào trang hoặc khi refreshKey đổi
        loadData();

        // 2. Cài đặt tự động cập nhật mỗi 10 giây
        const interval = setInterval(loadData, 10000);

        // Dọn dẹp khi thoát trang
        return () => clearInterval(interval);
    }, [refreshKey]); // <--- Chỉ chạy lại khi refreshKey thay đổi
    // -------------------------------------------------------

    // Mở Modal xác nhận xóa
    const openDeleteConfirm = (id) => {
        setDeleteId(id);
        setShowModal(true);
    };

    // Xử lý Xóa thật
    const confirmDelete = async () => {
        if (!deleteId) return;

        try {
            await dashboardService.deleteActivity(deleteId);

            toast.success("Đã xóa hoạt động thành công!", {
                style: {
                    border: '1px solid #10B981',
                    padding: '16px',
                    color: '#065F46',
                    background: '#D1FAE5',
                },
                iconTheme: {
                    primary: '#10B981',
                    secondary: '#FFFAEE',
                },
            });

            // Mẹo: Chỉ cần đổi refreshKey, useEffect ở trên sẽ tự chạy lại để load dữ liệu mới
            setRefreshKey(prev => prev + 1);
            setShowModal(false);
        } catch (error) {
            console.error("Lỗi xóa:", error);
            toast.error("Không thể xóa. Có lỗi xảy ra!");
        }
    };

    return (
        <div className="space-y-8 pb-10 animate-fade-in relative">

            {/* Header */}
            <div className="flex justify-between items-end">
                <div>
                    <h1 className="text-3xl font-black text-slate-800">Tổng quan hệ thống</h1>
                    <p className="text-slate-500 mt-1">Dữ liệu thực tế từ Database (PostgreSQL)</p>
                </div>
                <div className="text-right hidden sm:block">
                    <p className="text-sm font-bold text-slate-600 flex items-center gap-2 justify-end">
                        <span className="w-2 h-2 rounded-full bg-green-500 animate-pulse"></span>
                        Đang cập nhật
                    </p>
                </div>
            </div>

            {/* Các thẻ thống kê */}
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
                <div className="bg-white/80 backdrop-blur-xl p-6 rounded-3xl shadow-sm border border-white/50">
                    <div className="p-3 bg-blue-50 rounded-2xl text-blue-600 w-fit mb-4">
                        <Video className="w-6 h-6" />
                    </div>
                    <h3 className="text-slate-500 text-sm font-medium">Tổng video đã quét</h3>
                    <p className="text-3xl font-black text-slate-800 mt-1">{stats.total_videos}</p>
                </div>

                <div className="bg-white/80 backdrop-blur-xl p-6 rounded-3xl shadow-sm border border-white/50">
                    <div className="p-3 bg-red-50 rounded-2xl text-red-600 w-fit mb-4">
                        <AlertTriangle className="w-6 h-6" />
                    </div>
                    <h3 className="text-slate-500 text-sm font-medium">Phát hiện bạo lực</h3>
                    <p className="text-3xl font-black text-slate-800 mt-1">{stats.total_violence}</p>
                </div>

                <div className="bg-white/80 backdrop-blur-xl p-6 rounded-3xl shadow-sm border border-white/50">
                    <div className="p-3 bg-purple-50 rounded-2xl text-purple-600 w-fit mb-4">
                        <Activity className="w-6 h-6" />
                    </div>
                    <h3 className="text-slate-500 text-sm font-medium">Độ chính xác TB</h3>
                    <p className="text-3xl font-black text-slate-800 mt-1">{stats.avg_confidence}%</p>
                </div>

                <div className="bg-white/80 backdrop-blur-xl p-6 rounded-3xl shadow-sm border border-white/50">
                    <div className="p-3 bg-orange-50 rounded-2xl text-orange-600 w-fit mb-4">
                        <HardDrive className="w-6 h-6" />
                    </div>
                    <h3 className="text-slate-500 text-sm font-medium">Trạng thái Server</h3>
                    <p className="text-lg font-bold text-green-600 mt-2">Ổn định</p>
                </div>
            </div>

            {/* Biểu đồ & Danh sách */}
            <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
                {/* Biểu đồ */}
                <div className="lg:col-span-2 bg-white/80 backdrop-blur-xl p-8 rounded-3xl shadow-sm border border-white/50">
                    <h2 className="text-xl font-bold text-slate-800 mb-8">Thống kê 7 ngày qua</h2>
                    <div className="h-[300px] w-full">
                        <ResponsiveContainer width="100%" height="100%">
                            <BarChart data={stats.chart_data} barGap={8}>
                                <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#E2E8F0" />
                                <XAxis dataKey="name" axisLine={false} tickLine={false} />
                                <YAxis axisLine={false} tickLine={false} allowDecimals={false} />
                                <Tooltip cursor={{ fill: '#F1F5F9' }} />
                                <Bar dataKey="safe" name="An toàn" fill="#3B82F6" radius={[4, 4, 0, 0]} barSize={20} />
                                <Bar dataKey="violent" name="Bạo lực" fill="#EF4444" radius={[4, 4, 0, 0]} barSize={20} />
                            </BarChart>
                        </ResponsiveContainer>
                    </div>
                </div>

                {/* Danh sách Hoạt động */}
                <div className="bg-white/80 backdrop-blur-xl p-8 rounded-3xl shadow-sm border border-white/50">
                    <h2 className="text-xl font-bold text-slate-800 mb-6">Hoạt động mới nhất</h2>
                    <div className="space-y-6 overflow-y-auto max-h-[300px] custom-scrollbar">
                        {stats.recent_activities.length > 0 ? (
                            stats.recent_activities.map((item, index) => (
                                <div key={index} className="flex items-start gap-4 pb-6 border-b border-slate-100 last:border-0 last:pb-0 group relative">
                                    <div className={`w-10 h-10 rounded-xl flex items-center justify-center flex-shrink-0 
                    ${item.label === 'violent' ? 'bg-red-100 text-red-600' : 'bg-green-50 text-green-600'}`}>
                                        {item.label === 'violent' ? <AlertTriangle className="w-5 h-5" /> : <CheckCircle className="w-5 h-5" />}
                                    </div>
                                    <div className="flex-1 pr-6">
                                        <h4 className="text-sm font-bold text-slate-700 line-clamp-1">{item.video_name}</h4>
                                        <p className="text-xs text-slate-500 mt-1 flex items-center gap-1">
                                            <Clock className="w-3 h-3" /> {item.time}
                                        </p>
                                        <span className={`text-xs font-bold ${item.label === 'violent' ? 'text-red-500' : 'text-green-500'}`}>
                                            {item.label === 'violent' ? 'Phát hiện Bạo lực' : 'An toàn'}
                                        </span>
                                    </div>

                                    {/* Nút xóa */}
                                    <button
                                        onClick={() => openDeleteConfirm(item.id)}
                                        className="absolute right-0 top-0 p-2 text-slate-300 hover:text-red-500 hover:bg-red-50 rounded-full transition-all opacity-0 group-hover:opacity-100"
                                        title="Xóa hoạt động này"
                                    >
                                        <Trash2 className="w-4 h-4" />
                                    </button>
                                </div>
                            ))
                        ) : (
                            <p className="text-sm text-gray-400 text-center py-10">Chưa có dữ liệu.</p>
                        )}
                    </div>
                </div>
            </div>

            {/* Modal Xác Nhận Xóa */}
            {showModal && (
                <div className="fixed inset-0 z-50 flex items-center justify-center bg-slate-900/40 backdrop-blur-sm animate-fade-in">
                    <div className="bg-white p-6 rounded-2xl shadow-2xl w-full max-w-sm border border-white/60 transform scale-100 animate-scale-up">
                        <div className="flex flex-col items-center text-center">
                            <div className="w-14 h-14 bg-red-100 rounded-full flex items-center justify-center mb-4 text-red-600">
                                <AlertOctagon className="w-8 h-8" />
                            </div>
                            <h3 className="text-xl font-bold text-slate-800 mb-2">Xác nhận xóa?</h3>
                            <p className="text-slate-500 text-sm mb-6">
                                Bạn có chắc chắn muốn xóa hoạt động này khỏi lịch sử không? Hành động này không thể hoàn tác.
                            </p>
                            <div className="flex gap-3 w-full">
                                <button
                                    onClick={() => setShowModal(false)}
                                    className="flex-1 py-2.5 rounded-xl border border-slate-200 font-bold text-slate-600 hover:bg-slate-50 transition-colors"
                                >
                                    Hủy bỏ
                                </button>
                                <button
                                    onClick={confirmDelete}
                                    className="flex-1 py-2.5 rounded-xl bg-red-500 font-bold text-white hover:bg-red-600 shadow-lg shadow-red-200 transition-colors"
                                >
                                    Xóa ngay
                                </button>
                            </div>
                        </div>
                    </div>
                </div>
            )}

        </div>
    );
};

export default Dashboard;