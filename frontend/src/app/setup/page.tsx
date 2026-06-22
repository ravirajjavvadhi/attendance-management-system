"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { Building2, ArrowRight, Upload, Briefcase, GraduationCap, Calendar } from "lucide-react";

export default function SetupWorkspace() {
  const router = useRouter();
  const [step, setStep] = useState(1);
  const [loading, setLoading] = useState(false);

  const [formData, setFormData] = useState({
    name: "",
    type: "university",
    departments: "",
    academicYear: "2024-2025"
  });

  const handleNext = () => setStep(step + 1);
  
  const handleComplete = async () => {
    setLoading(true);
    // Submit to FastAPI backend...
    setTimeout(() => {
      router.push("/dashboard/principal");
    }, 1500);
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-background p-4">
      <div className="w-full max-w-xl">
        <div className="flex items-center gap-2 mb-12">
          <div className="w-8 h-8 rounded-lg bg-primary flex items-center justify-center">
            <span className="text-primary-foreground font-bold text-xl">E</span>
          </div>
          <span className="font-bold text-xl tracking-tight text-foreground">EduFlow</span>
        </div>

        <div className="space-y-8 animate-in fade-in slide-in-from-bottom-4 duration-500">
          <div>
            <div className="flex items-center gap-2 text-sm font-medium text-muted-foreground mb-2">
              Step {step} of 2
            </div>
            <h1 className="text-3xl font-bold tracking-tight text-foreground">
              {step === 1 ? "Create your workspace" : "Setup academic structure"}
            </h1>
            <p className="text-muted-foreground mt-2">
              {step === 1 ? "Let's set up a digital home for your institution." : "Define your departments and academic calendar."}
            </p>
          </div>

          {step === 1 ? (
            <div className="space-y-6">
              <div className="space-y-2">
                <label className="text-sm font-medium text-foreground">Institution Logo</label>
                <div className="border-2 border-dashed border-border rounded-xl p-8 flex flex-col items-center justify-center hover:bg-secondary/50 transition-colors cursor-pointer">
                  <div className="w-12 h-12 rounded-full bg-secondary flex items-center justify-center mb-3">
                    <Upload className="w-5 h-5 text-muted-foreground" />
                  </div>
                  <p className="text-sm font-medium">Click to upload logo</p>
                  <p className="text-xs text-muted-foreground mt-1">SVG, PNG, or JPG (max. 2MB)</p>
                </div>
              </div>

              <div className="space-y-2">
                <label className="text-sm font-medium text-foreground">Institution Name</label>
                <div className="relative">
                  <Building2 className="absolute left-3 top-2.5 h-5 w-5 text-muted-foreground" />
                  <input 
                    type="text" 
                    value={formData.name}
                    onChange={e => setFormData({...formData, name: e.target.value})}
                    placeholder="e.g. Stanford University"
                    className="w-full bg-background border border-input rounded-lg pl-10 pr-3 py-2.5 text-foreground focus:ring-2 focus:ring-ring focus:border-transparent transition-all outline-none"
                  />
                </div>
              </div>

              <div className="space-y-2">
                <label className="text-sm font-medium text-foreground">Institution Type</label>
                <div className="grid grid-cols-2 gap-4">
                  {['university', 'school'].map((type) => (
                    <label 
                      key={type}
                      className={`flex items-center gap-3 p-4 border rounded-xl cursor-pointer transition-all ${formData.type === type ? 'border-primary bg-primary/5 ring-1 ring-primary' : 'border-border hover:border-muted-foreground/30'}`}
                    >
                      <input 
                        type="radio" 
                        name="type" 
                        value={type} 
                        checked={formData.type === type}
                        onChange={(e) => setFormData({...formData, type: e.target.value})}
                        className="hidden" 
                      />
                      {type === 'university' ? <Briefcase className="w-5 h-5 text-blue-500" /> : <GraduationCap className="w-5 h-5 text-green-500" />}
                      <span className="font-medium capitalize">{type}</span>
                    </label>
                  ))}
                </div>
              </div>

              <button 
                onClick={handleNext}
                disabled={!formData.name}
                className="w-full flex items-center justify-center gap-2 bg-primary text-primary-foreground hover:bg-primary/90 font-medium py-3 px-4 rounded-lg transition-colors disabled:opacity-50 mt-4"
              >
                Continue <ArrowRight className="w-4 h-4" />
              </button>
            </div>
          ) : (
            <div className="space-y-6">
              <div className="space-y-2">
                <label className="text-sm font-medium text-foreground">Departments (comma separated)</label>
                <input 
                  type="text" 
                  value={formData.departments}
                  onChange={e => setFormData({...formData, departments: e.target.value})}
                  placeholder="e.g. Computer Science, Mechanical, Arts"
                  className="w-full bg-background border border-input rounded-lg px-4 py-2.5 text-foreground focus:ring-2 focus:ring-ring focus:border-transparent transition-all outline-none"
                />
              </div>

              <div className="space-y-2">
                <label className="text-sm font-medium text-foreground">Current Academic Year</label>
                <div className="relative">
                  <Calendar className="absolute left-3 top-2.5 h-5 w-5 text-muted-foreground" />
                  <select 
                    value={formData.academicYear}
                    onChange={e => setFormData({...formData, academicYear: e.target.value})}
                    className="w-full bg-background border border-input rounded-lg pl-10 pr-3 py-2.5 text-foreground focus:ring-2 focus:ring-ring focus:border-transparent transition-all appearance-none outline-none"
                  >
                    <option>2023-2024</option>
                    <option>2024-2025</option>
                    <option>2025-2026</option>
                  </select>
                </div>
              </div>

              <div className="flex gap-4 pt-4">
                <button 
                  onClick={() => setStep(1)}
                  className="px-6 py-3 border border-input rounded-lg font-medium hover:bg-secondary transition-colors"
                >
                  Back
                </button>
                <button 
                  onClick={handleComplete}
                  disabled={loading || !formData.departments}
                  className="flex-1 flex items-center justify-center gap-2 bg-primary text-primary-foreground hover:bg-primary/90 font-medium py-3 px-4 rounded-lg transition-colors disabled:opacity-70"
                >
                  {loading ? "Creating Workspace..." : "Complete Setup"}
                </button>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
