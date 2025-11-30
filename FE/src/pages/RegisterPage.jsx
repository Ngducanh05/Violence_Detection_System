import { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import toast from 'react-hot-toast';
import { UserPlus, User, Mail, Lock } from 'lucide-react';
import { register } from '../services/authService'; // <--- Import Service

const RegisterPage = () => {
    const navigate = useNavigate();
    const [formData, setFormData] = useState({ name: '', email: '', password: '' });

    const handleSubmit = async (e) => {
        e.preventDefault();

        if (formData.password.length < 6) {
            toast.error("Mật khẩu phải có ít nhất 6 ký tự!");
            return;
        }

        const loadingToast = toast.loading("Đang xử lý đăng ký...");

        try {
            // CŨ: await axios.post("http://...", formData);
            // MỚI: Gọi qua Service gọn gàng
           await register(formData.name, formData.email, formData.password);



            toast.dismiss(loadingToast);
            toast.success("Đăng ký thành công! Hãy đăng nhập ngay.", {
                duration: 4000,
                style: { border: '1px solid #22c55e', padding: '16px', color: '#15803d' },
                iconTheme: { primary: '#22c55e', secondary: '#FFFAEE' },
            });

            navigate('/login');
        } catch (err) {
            toast.dismiss(loadingToast);
            const errorMsg = err.response?.data?.detail || "Đăng ký thất bại!";
            toast.error(errorMsg);
        }
    };

    return (
        <div className="min-h-screen flex items-center justify-center p-4">
            <div className="bg-white/80 backdrop-blur-xl p-8 rounded-3xl shadow-2xl w-full max-w-md border border-white/60 animate-fade-in">
                <div className="text-center mb-8">
                    <div className="w-16 h-16 bg-green-500 rounded-2xl flex items-center justify-center mx-auto mb-4 shadow-lg shadow-green-200">
                        <UserPlus className="w-8 h-8 text-white" />
                    </div>
                    <h1 className="text-3xl font-black text-slate-800">Tạo tài khoản</h1>
                    <p className="text-slate-500 mt-2">Tham gia hệ thống Violence AI</p>
                </div>

                <form onSubmit={handleSubmit} className="space-y-5">
                    <div className="relative">
                        <User className="absolute left-4 top-3.5 w-5 h-5 text-gray-400" />
                        <input
                            type="text" placeholder="Họ và tên" required
                            className="w-full pl-12 pr-4 py-3 rounded-xl border border-gray-200 focus:border-green-500 focus:ring-2 focus:ring-green-200 outline-none transition-all"
                            onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                        />
                    </div>
                    <div className="relative">
                        <Mail className="absolute left-4 top-3.5 w-5 h-5 text-gray-400" />
                        <input
                            type="email" placeholder="Email" required
                            className="w-full pl-12 pr-4 py-3 rounded-xl border border-gray-200 focus:border-green-500 focus:ring-2 focus:ring-green-200 outline-none transition-all"
                            onChange={(e) => setFormData({ ...formData, email: e.target.value })}
                        />
                    </div>
                    <div className="relative">
                        <Lock className="absolute left-4 top-3.5 w-5 h-5 text-gray-400" />
                        <input
                            type="password" placeholder="Mật khẩu (tối thiểu 6 ký tự)" required
                            className="w-full pl-12 pr-4 py-3 rounded-xl border border-gray-200 focus:border-green-500 focus:ring-2 focus:ring-green-200 outline-none transition-all"
                            onChange={(e) => setFormData({ ...formData, password: e.target.value })}
                        />
                    </div>

                    <button type="submit" className="w-full py-3 rounded-xl bg-green-500 text-white font-bold text-lg shadow-lg hover:bg-green-600 transition-all transform active:scale-95">
                        Đăng Ký
                    </button>
                </form>

                <p className="text-center mt-6 text-slate-600">
                    Đã có tài khoản? <Link to="/login" className="text-green-600 font-bold hover:underline">Đăng nhập ngay</Link>
                </p>
            </div>
        </div>
    );
};

export default RegisterPage;