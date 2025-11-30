import { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { login } from "../services/authService";
import toast from 'react-hot-toast'; // Import thư viện thông báo
import { LogIn, Mail, Lock, Eye, EyeOff } from 'lucide-react';

const LoginPage = () => {
    const navigate = useNavigate();
    const [formData, setFormData] = useState({ email: '', password: '' });
    const [showPass, setShowPass] = useState(false);

    const handleSubmit = async (e) => {
        e.preventDefault();
        const loadingToast = toast.loading("Đang xác thực tài khoản...");

        try {
            const res = await login(formData.email, formData.password);

            localStorage.setItem("token", res.access_token);
            localStorage.setItem("currentUser", JSON.stringify(res.user));


            // Tắt loading, hiện thành công
            toast.dismiss(loadingToast);
            toast.success("Đăng nhập thành công! Chào mừng trở lại.", {
                duration: 3000,
                style: {
                    border: '1px solid #3b82f6',
                    padding: '16px',
                    color: '#1d4ed8',
                },
                iconTheme: {
                    primary: '#3b82f6',
                    secondary: '#FFFAEE',
                },
            });

            // Chuyển hướng và reload để cập nhật Navbar
            navigate('/');
            window.location.reload();
        } catch (err) {
            // Tắt loading, hiện lỗi
            toast.dismiss(loadingToast);
            const msg = err.response?.data?.detail || "Đăng nhập thất bại. Vui lòng kiểm tra lại!";
            toast.error(msg);
        }
    };

    return (
        <div className="min-h-screen flex items-center justify-center p-4">
            <div className="bg-white/80 backdrop-blur-xl p-8 rounded-3xl shadow-2xl w-full max-w-md border border-white/60 animate-fade-in">
                <div className="text-center mb-8">
                    <div className="w-16 h-16 bg-blue-600 rounded-2xl flex items-center justify-center mx-auto mb-4 shadow-lg shadow-blue-200">
                        <LogIn className="w-8 h-8 text-white" />
                    </div>
                    <h1 className="text-3xl font-black text-slate-800">Chào mừng trở lại</h1>
                    <p className="text-slate-500 mt-2">Đăng nhập để quản lý hệ thống</p>
                </div>

                <form onSubmit={handleSubmit} className="space-y-5">
                    <div className="relative">
                        <Mail className="absolute left-4 top-3.5 w-5 h-5 text-gray-400" />
                        <input
                            type="email" placeholder="Email của bạn" required
                            className="w-full pl-12 pr-4 py-3 rounded-xl border border-gray-200 focus:border-blue-500 focus:ring-2 focus:ring-blue-200 outline-none transition-all"
                            onChange={(e) => setFormData({ ...formData, email: e.target.value })}
                        />
                    </div>
                    <div className="relative">
                        <Lock className="absolute left-4 top-3.5 w-5 h-5 text-gray-400" />
                        <input
                            type={showPass ? "text" : "password"} placeholder="Mật khẩu" required
                            className="w-full pl-12 pr-12 py-3 rounded-xl border border-gray-200 focus:border-blue-500 focus:ring-2 focus:ring-blue-200 outline-none transition-all"
                            onChange={(e) => setFormData({ ...formData, password: e.target.value })}
                        />
                        <button type="button" onClick={() => setShowPass(!showPass)} className="absolute right-4 top-3.5 text-gray-400 hover:text-blue-600">
                            {showPass ? <EyeOff className="w-5 h-5" /> : <Eye className="w-5 h-5" />}
                        </button>
                    </div>

                    <button type="submit" className="w-full py-3 rounded-xl bg-blue-600 text-white font-bold text-lg shadow-lg hover:bg-blue-700 transition-all transform active:scale-95">
                        Đăng Nhập
                    </button>
                </form>

                <p className="text-center mt-6 text-slate-600">
                    Bạn chưa có tài khoản? <Link to="/register" className="text-blue-600 font-bold hover:underline">Tạo tài khoản mới</Link>
                </p>
            </div>
        </div>
    );
};

export default LoginPage;