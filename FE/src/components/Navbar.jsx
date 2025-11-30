import { useState, useEffect } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { Bell, Search, User, X, LogIn, Clock } from 'lucide-react';
import { auditService } from '../services/auditService'; // <--- Import Service

const Navbar = () => {
    const [showNoti, setShowNoti] = useState(false);
    const [notifications, setNotifications] = useState([]);
    const navigate = useNavigate();

    const [currentUser] = useState(() => {
        const savedUser = localStorage.getItem('currentUser');
        return savedUser ? JSON.parse(savedUser) : null;
    });

    useEffect(() => {
        if (currentUser) {
            // CŨ: axios.get(...)
            // MỚI: Gọi qua Service
            auditService.getMyNotifications(currentUser.user_id)
                .then(res => {
                    const formattedNotis = res.data.map(log => ({
                        id: log.log_id,
                        text: log.action,
                        time: new Date(log.created_at).toLocaleTimeString('vi-VN', { hour: '2-digit', minute: '2-digit' }),
                        type: 'info'
                    }));
                    setNotifications(formattedNotis);
                })
                .catch(err => {
                    console.error("Lỗi lấy thông báo:", err);
                    setNotifications([]);
                });
        }
    }, [currentUser]);

    return (
        <div className="h-16 bg-white/70 backdrop-blur-md border-b border-white/40 flex items-center justify-between px-8 sticky top-0 z-10 shadow-sm transition-all duration-300">
            <div className="relative w-96 group">
                <span className="absolute inset-y-0 left-0 pl-3 flex items-center transition-colors group-focus-within:text-blue-500">
                    <Search className="h-5 w-5 text-gray-400" />
                </span>
                <input type="text" className="w-full pl-10 pr-4 py-2 rounded-xl border border-gray-200/60 bg-white/50 focus:bg-white focus:border-blue-500 outline-none text-sm transition-all duration-300" placeholder="Tìm kiếm video, dự án..." />
            </div>

            <div className="flex items-center gap-6 relative">
                <button onClick={() => setShowNoti(!showNoti)} className="relative p-2 text-gray-500 hover:bg-white rounded-full transition-all hover:text-blue-600 hover:shadow-md">
                    <Bell className="w-5 h-5" />
                    {notifications.length > 0 && (
                        <span className="absolute top-1 right-1 w-2 h-2 bg-red-500 rounded-full border-2 border-white animate-pulse"></span>
                    )}
                </button>

                {showNoti && (
                    <div className="absolute top-14 right-0 w-80 bg-white/90 backdrop-blur-xl rounded-2xl shadow-2xl border border-white/50 p-4 animate-fade-in-up z-50">
                        <div className="flex justify-between items-center mb-3 pb-2 border-b border-gray-100">
                            <h4 className="font-bold text-slate-700">Hoạt động của bạn</h4>
                            <button onClick={() => setShowNoti(false)} className="hover:bg-red-50 p-1 rounded-full text-slate-400 hover:text-red-500 transition-colors">
                                <X className="w-4 h-4" />
                            </button>
                        </div>
                        <div className="space-y-2 max-h-64 overflow-y-auto custom-scrollbar">
                            {notifications.length > 0 ? (
                                notifications.map(n => (
                                    <div key={n.id} className="text-sm p-3 rounded-xl bg-white border border-slate-50 shadow-sm hover:shadow-md transition-all flex gap-3 items-start">
                                        <div className="mt-1 min-w-[6px] h-[6px] rounded-full bg-blue-500"></div>
                                        <div>
                                            <p className="font-semibold text-slate-700 text-xs">{n.text}</p>
                                            <p className="text-[10px] text-slate-400 mt-1 flex items-center gap-1">
                                                <Clock className="w-3 h-3" /> {n.time}
                                            </p>
                                        </div>
                                    </div>
                                ))
                            ) : (
                                <p className="text-center text-xs text-slate-400 py-4">Chưa có thông báo nào</p>
                            )}
                        </div>
                    </div>
                )}

                <div className="flex items-center gap-3 pl-6 border-l border-gray-300/50">
                    {currentUser ? (
                        <>
                            <div className="text-right hidden md:block">
                                <p className="text-sm font-bold text-slate-800">{currentUser.name}</p>
                                <p className="text-[10px] font-bold text-blue-600 bg-blue-50 px-2 py-0.5 rounded-full uppercase inline-block">{currentUser.role}</p>
                            </div>
                            <div className="w-10 h-10 bg-gradient-to-br from-blue-500 to-cyan-400 rounded-full flex items-center justify-center border-2 border-white shadow-md cursor-pointer hover:scale-105 transition-transform">
                                <span className="text-white font-bold text-lg">{currentUser.name.charAt(0).toUpperCase()}</span>
                            </div>
                        </>
                    ) : (
                        <button onClick={() => navigate('/login')} className="flex items-center gap-2 px-5 py-2.5 bg-slate-800 text-white rounded-xl font-bold text-sm hover:bg-slate-700 hover:shadow-lg transition-all transform hover:-translate-y-0.5">
                            <LogIn className="w-4 h-4" /> Đăng Nhập
                        </button>
                    )}
                </div>
            </div>
        </div>
    );
};

export default Navbar;