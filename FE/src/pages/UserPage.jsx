import { useState, useEffect } from 'react';
import { User, Mail, Shield, CheckCircle, Clock } from 'lucide-react';
import { userService } from '../services/userService'; // <--- Import Service

const UserPage = () => {
    const [users, setUsers] = useState([]);
    const [currentUser] = useState(() => {
        const storedUser = localStorage.getItem('currentUser');
        return storedUser ? JSON.parse(storedUser) : null;
    });

    useEffect(() => {
        // Chỉ gọi API lấy danh sách nếu là Admin
        if (currentUser && currentUser.role === 'admin') {
            // MỚI: Gọi qua Service
            userService.getAllUsers()
                .then(res => setUsers(res.data))
                .catch(err => console.error(err));
        }
    }, [currentUser]);

    if (!currentUser) return null;

    // TRƯỜNG HỢP 1: USER THƯỜNG -> HIỆN PROFILE
    if (currentUser.role !== 'admin') {
        return (
            <div className="w-full flex justify-center items-center min-h-[80vh] animate-fade-in">
                <div className="bg-white/80 backdrop-blur-xl rounded-3xl shadow-2xl border border-white/60 w-full max-w-2xl overflow-hidden">
                    <div className="h-32 bg-gradient-to-r from-blue-600 to-cyan-500 relative">
                        <div className="absolute -bottom-12 left-8 p-1 bg-white rounded-full">
                            <div className="w-24 h-24 bg-slate-200 rounded-full flex items-center justify-center text-4xl font-bold text-slate-500 border-4 border-white shadow-md">
                                {currentUser.name.charAt(0).toUpperCase()}
                            </div>
                        </div>
                    </div>
                    <div className="pt-16 pb-8 px-8">
                        <div className="flex justify-between items-start">
                            <div>
                                <h1 className="text-3xl font-black text-slate-800">{currentUser.name}</h1>
                                <span className="inline-flex items-center gap-1 px-3 py-1 rounded-full bg-blue-100 text-blue-700 text-xs font-bold mt-2 uppercase">
                                    <Shield className="w-3 h-3" /> {currentUser.role}
                                </span>
                            </div>
                            <button className="px-4 py-2 border border-slate-200 rounded-xl text-slate-600 font-bold text-sm hover:bg-slate-50 transition-all">
                                Chỉnh sửa
                            </button>
                        </div>
                        <div className="mt-8 grid grid-cols-1 md:grid-cols-2 gap-6">
                            <div className="p-4 bg-slate-50 rounded-2xl border border-slate-100">
                                <p className="text-xs font-bold text-slate-400 uppercase mb-1">Email đăng nhập</p>
                                <div className="flex items-center gap-2 text-slate-700 font-medium"><Mail className="w-4 h-4 text-blue-500" />{currentUser.email}</div>
                            </div>
                            <div className="p-4 bg-slate-50 rounded-2xl border border-slate-100">
                                <p className="text-xs font-bold text-slate-400 uppercase mb-1">Mã định danh (ID)</p>
                                <div className="flex items-center gap-2 text-slate-700 font-medium"><User className="w-4 h-4 text-blue-500" />User #{currentUser.user_id}</div>
                            </div>
                            <div className="p-4 bg-slate-50 rounded-2xl border border-slate-100">
                                <p className="text-xs font-bold text-slate-400 uppercase mb-1">Trạng thái</p>
                                <div className="flex items-center gap-2 text-green-600 font-bold"><CheckCircle className="w-4 h-4" />Đang hoạt động</div>
                            </div>
                            <div className="p-4 bg-slate-50 rounded-2xl border border-slate-100">
                                <p className="text-xs font-bold text-slate-400 uppercase mb-1">Hoạt động gần nhất</p>
                                <div className="flex items-center gap-2 text-slate-700 font-medium"><Clock className="w-4 h-4 text-blue-500" />Vừa truy cập</div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        );
    }

    // TRƯỜNG HỢP 2: ADMIN -> HIỆN DANH SÁCH
    return (
        <div className="space-y-6 animate-fade-in">
            <div className="flex justify-between items-center">
                <h1 className="text-3xl font-black text-slate-800">Quản lý người dùng</h1>
                <div className="px-4 py-2 bg-blue-100 text-blue-700 rounded-xl text-sm font-bold">Admin View</div>
            </div>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                {users.map((user) => (
                    <div key={user.user_id} className="bg-white/80 backdrop-blur-xl p-6 rounded-2xl border border-white/60 shadow-sm hover:shadow-md transition-all group">
                        <div className="flex items-center gap-4 mb-4">
                            <div className={`w-12 h-12 rounded-full flex items-center justify-center text-white font-bold text-lg shadow-md ${user.role === 'admin' ? 'bg-purple-500' : 'bg-blue-500'}`}>
                                {user.name.charAt(0).toUpperCase()}
                            </div>
                            <div>
                                <h3 className="font-bold text-slate-800 group-hover:text-blue-600 transition-colors">{user.name}</h3>
                                <p className="text-xs text-slate-400">ID: {user.user_id}</p>
                            </div>
                        </div>
                        <div className="space-y-2 text-sm text-slate-600">
                            <div className="flex items-center gap-2"><Mail className="w-4 h-4 text-slate-400" /> {user.email}</div>
                            <div className="flex items-center gap-2">
                                <Shield className="w-4 h-4 text-slate-400" />
                                <span className={`uppercase font-bold text-[10px] px-2 py-0.5 rounded ${user.role === 'admin' ? 'bg-purple-100 text-purple-700' : 'bg-slate-100 text-slate-600'}`}>{user.role}</span>
                            </div>
                        </div>
                    </div>
                ))}
            </div>
        </div>
    );
};

export default UserPage;