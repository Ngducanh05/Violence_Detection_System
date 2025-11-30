import { Camera, MapPin, MoreVertical } from 'lucide-react';

const ProjectsPage = () => {
    const projects = [
        { id: 1, name: "Khu vực Cổng chính", location: "Tầng 1 - Sảnh A", status: "active" },
        { id: 2, name: "Nhà xe sinh viên", location: "Tầng hầm B1", status: "active" },
        { id: 3, name: "Hành lang Thư viện", location: "Tầng 3 - Khu C", status: "inactive" },
    ];

    return (
        <div className="space-y-6 animate-fade-in">
            <h1 className="text-3xl font-black text-slate-800">Dự án Camera</h1>

            <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                {projects.map((cam) => (
                    <div key={cam.id} className="group bg-white p-4 rounded-2xl border border-slate-100 shadow-sm hover:shadow-lg transition-all cursor-pointer">
                        <div className="relative aspect-video bg-black rounded-xl mb-4 overflow-hidden">
                            <div className="absolute inset-0 flex items-center justify-center text-white/20">
                                <Camera className="w-12 h-12" />
                            </div>
                            <span className={`absolute top-2 right-2 w-3 h-3 rounded-full ${cam.status === 'active' ? 'bg-green-500 animate-pulse' : 'bg-red-500'}`}></span>
                        </div>
                        <div className="flex justify-between items-start">
                            <div>
                                <h3 className="font-bold text-slate-700 group-hover:text-blue-600 transition-colors">{cam.name}</h3>
                                <p className="text-xs text-slate-400 flex items-center gap-1 mt-1">
                                    <MapPin className="w-3 h-3" /> {cam.location}
                                </p>
                            </div>
                            <button className="text-slate-300 hover:text-slate-600"><MoreVertical className="w-4 h-4" /></button>
                        </div>
                    </div>
                ))}
            </div>
        </div>
    );
};

export default ProjectsPage;