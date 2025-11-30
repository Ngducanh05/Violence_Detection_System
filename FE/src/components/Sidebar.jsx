import { useState } from 'react';
import { Home, Video, Eye, History, Users, LogOut } from 'lucide-react';
import { Link, useLocation, useNavigate } from 'react-router-dom';
import toast from 'react-hot-toast';

const Sidebar = () => {
    const location = useLocation();
    const navigate = useNavigate();

    // Kiểm tra trạng thái đăng nhập
    const [isLoggedIn, setIsLoggedIn] = useState(() => {
        return !!localStorage.getItem('currentUser');
    });

    // Lấy role của user (để đổi tên menu)
    const userRole = (() => {
        const user = localStorage.getItem('currentUser');
        return user ? JSON.parse(user).role : 'annotator';
    })();

    const handleLogout = () => {
        toast((t) => (
            <div className="flex flex-col gap-3 min-w-[200px]">
                <span className="font-bold text-slate-700 text-sm">Bạn có chắc muốn đăng xuất?</span>
                <div className="flex gap-2 justify-end">
                    <button
                        onClick={() => toast.dismiss(t.id)}
                        className="bg-slate-100 text-slate-600 px-3 py-1.5 rounded-lg text-xs font-bold hover:bg-slate-200 transition-colors"
                    >
                        Hủy
                    </button>
                    <button
                        onClick={() => {
                            localStorage.removeItem('currentUser');
                            setIsLoggedIn(false);
                            toast.dismiss(t.id);
                            toast.success("Đã đăng xuất thành công!");
                            navigate('/login');
                            window.location.reload();
                        }}
                        className="bg-red-500 text-white px-3 py-1.5 rounded-lg text-xs font-bold hover:bg-red-600 transition-colors shadow-sm"
                    >
                        Đăng xuất
                    </button>
                </div>
            </div>
        ), {
            duration: 5000,
            icon: '👋',
            style: {
                border: '1px solid #E2E8F0',
                boxShadow: '0 4px 6px -1px rgba(0, 0, 0, 0.1)',
            },
        });
    };

    const menuItems = [
        { name: 'Dashboard', icon: Home, path: '/' },
        { name: 'Live Detect', icon: Video, path: '/live' },
        { name: 'Nhận diện AI', icon: Eye, path: '/detect' },
        { name: 'Lịch sử & Audit', icon: History, path: '/audit' },
        // Logic đổi tên menu dựa trên quyền
        {
            name: userRole === 'admin' ? 'Quản lý User' : 'Hồ sơ cá nhân',
            icon: Users,
            path: '/users'
        },
    ];

    return (
        <div className="w-64 h-screen bg-white/70 backdrop-blur-md border-r border-white/40 flex flex-col shadow-lg fixed left-0 top-0 z-20">

            <div className="h-16 flex items-center px-8 border-b border-gray-200/50">
                <div className="w-8 h-8 bg-gradient-to-br from-blue-600 to-cyan-500 rounded-lg mr-3 flex items-center justify-center shadow-blue-500/30 shadow-lg">
                    <Eye className="text-white w-5 h-5" />
                </div>
                <span className="text-xl font-bold text-slate-800 tracking-tight">Violence AI</span>
            </div>

            <nav className="flex-1 px-4 py-6 space-y-2">
                {menuItems.map((item) => {
                    const isActive = location.pathname === item.path;
                    return (
                        <Link
                            key={item.name}
                            to={item.path}
                            className={`flex items-center px-4 py-3 rounded-xl transition-all duration-300 group
                ${isActive
                                    ? 'bg-blue-600 text-white shadow-md shadow-blue-500/30 translate-x-1'
                                    : 'text-slate-600 hover:bg-white/50 hover:text-blue-600 hover:translate-x-1'
                                }`}
                        >
                            <item.icon className={`w-5 h-5 mr-3 transition-transform duration-300 ${!isActive && 'group-hover:scale-110'}`} />
                            <span className="font-medium">{item.name}</span>
                        </Link>
                    );
                })}
            </nav>

            {isLoggedIn && (
                <div className="p-4 border-t border-gray-200/50 space-y-2">
                    <button
                        onClick={handleLogout}
                        className="flex items-center w-full px-4 py-3 text-slate-600 hover:bg-red-50/80 hover:text-red-600 rounded-xl transition-all duration-200 hover:shadow-sm group"
                    >
                        <LogOut className="w-5 h-5 mr-3 group-hover:rotate-180 transition-transform duration-300" />
                        <span className="font-medium">Đăng xuất</span>
                    </button>
                </div>
            )}
        </div>
    );
};

export default Sidebar;