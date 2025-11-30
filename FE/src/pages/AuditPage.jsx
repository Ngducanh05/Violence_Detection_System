import { useState, useEffect } from 'react';
import { Filter } from 'lucide-react';
import { auditService } from '../services/auditService';

const AuditPage = () => {
    const [logs, setLogs] = useState([]);

    useEffect(() => {
        auditService.getMyResults()
            .then(res => setLogs(res.data))
            .catch(err => console.error("Lỗi tải dữ liệu:", err));
    }, []);

    return (
        <div className="space-y-6 animate-fade-in">

            {/* Header */}
            <div className="flex justify-between items-center">
                <h1 className="text-3xl font-black text-slate-800">Lịch sử & Audit</h1>
                <button className="px-4 py-2 bg-white border border-slate-200 rounded-lg text-sm font-bold text-slate-600 hover:bg-slate-50 flex items-center gap-2">
                    <Filter className="w-4 h-4" /> Lọc dữ liệu
                </button>
            </div>

            {/* Table */}
            <div className="bg-white/80 backdrop-blur-xl rounded-2xl border border-white/60 shadow-sm overflow-hidden">
                <table className="w-full text-left border-collapse">
                    <thead>
                        <tr className="bg-slate-50/50 border-b border-slate-100 text-xs uppercase text-slate-500 font-bold tracking-wider">
                            <th className="p-4">ID</th>
                            <th className="p-4">Thời gian</th>
                            <th className="p-4">Kết quả</th>
                            <th className="p-4">Độ tin cậy</th>
                            <th className="p-4">Hành động</th>
                        </tr>
                    </thead>

                    <tbody className="text-sm">
                        {logs.map((log, index) => (
                            <tr key={index} className="border-b border-slate-50 hover:bg-blue-50/30 transition-colors">

                                {/* Video ID */}
                                <td className="p-4 font-mono text-slate-400">#{log.video_id}</td>

                                {/* Thời gian cuối */}
                                <td className="p-4 text-slate-600">
                                    {log.last_time ? new Date(log.last_time).toLocaleString() : "—"}
                                </td>

                                {/* Nhãn tổng hợp */}
                                <td className="p-4">
                                    <span className={`px-2 py-1 rounded-full text-xs font-bold 
                                        ${log.is_violent ? "bg-red-100 text-red-600" : "bg-green-100 text-green-600"}`}>
                                        {log.is_violent ? "BẠO LỰC" : "AN TOÀN"}
                                    </span>
                                </td>

                                {/* Confidence */}
                                <td className="p-4 font-bold text-slate-700">
                                    {Math.round((log.avg_confidence || 0) * 100)}%
                                </td>

                                <td className="p-4 text-blue-600 hover:underline cursor-pointer">
                                    Xem chi tiết
                                </td>
                            </tr>
                        ))}
                    </tbody>
                </table>

                {logs.length === 0 && (
                    <div className="p-8 text-center text-slate-400">Chưa có dữ liệu lịch sử</div>
                )}
            </div>
        </div>
    );
};

export default AuditPage;
