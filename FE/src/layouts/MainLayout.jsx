import { Outlet } from 'react-router-dom';
import Sidebar from '../components/Sidebar';
import Navbar from '../components/Navbar';
import bgImage from '../assets/bg.jpg'; // Import hình nền

const MainLayout = () => {
    return (
        <div
            className="min-h-screen font-sans bg-cover bg-center bg-fixed relative"
            style={{ backgroundImage: `url(${bgImage})` }}
        >
            {/* Lớp phủ màu đen mờ để chữ dễ đọc hơn */}
            <div className="absolute inset-0 bg-slate-900/30 backdrop-blur-[2px] z-0"></div>

            {/* Nội dung chính */}
            <div className="relative z-10 flex">
                <Sidebar />
                <div className="flex-1 flex flex-col ml-64 transition-all duration-300">
                    <Navbar />
                    <main className="p-8">
                        <div className="max-w-7xl mx-auto animate-fade-in">
                            <Outlet />
                        </div>
                    </main>
                </div>
            </div>
        </div>
    );
};

export default MainLayout;