"use client";

import { useState } from "react";
import { Search, Plus, Filter, Download, MoreHorizontal, FileSpreadsheet, Zap, UserPlus } from "lucide-react";

export default function StudentManagement() {
  const [search, setSearch] = useState("");
  const [showSmartOnboard, setShowSmartOnboard] = useState(false);
  const [rollNumbersInput, setRollNumbersInput] = useState("");
  const [selectedClass, setSelectedClass] = useState("10th");
  const [selectedSection, setSelectedSection] = useState("A");

  const handleSmartOnboard = (e: React.FormEvent) => {
    e.preventDefault();
    const rolls = rollNumbersInput.split(",").map(r => r.trim()).filter(r => r);
    setTimeout(() => {
      alert(`Successfully generated ${rolls.length} students in ${selectedClass} Section ${selectedSection}!`);
      setShowSmartOnboard(false);
      setRollNumbersInput("");
    }, 1000);
  };

  const students = [
    { id: "101", roll: "1", name: "John Doe", class: "10th A", status: "Active", attendance: "85%" },
    { id: "102", roll: "2", name: "Jane Smith", class: "10th A", status: "Active", attendance: "92%" },
    { id: "103", roll: "3", name: "Mike Johnson", class: "10th B", status: "Inactive", attendance: "45%" },
    { id: "104", roll: "4", name: "Emily Davis", class: "11th Sci", status: "Active", attendance: "98%" },
    { id: "105", roll: "5", name: "Chris Brown", class: "9th A", status: "Active", attendance: "76%" },
  ];

  return (
    <div className="space-y-8 animate-in fade-in slide-in-from-bottom-4 duration-500">
      <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4">
        <div>
          <h1 className="text-3xl font-bold tracking-tight text-foreground">Student Directory</h1>
          <p className="text-muted-foreground mt-1">Manage enrollments, transfers, and student records.</p>
        </div>
        <div className="flex gap-3">
          <button 
            onClick={() => setShowSmartOnboard(true)}
            className="flex items-center gap-2 bg-indigo-500/10 text-indigo-500 hover:bg-indigo-500/20 px-4 py-2 rounded-lg text-sm font-bold transition-colors"
          >
            <Zap className="w-4 h-4 fill-indigo-500" /> Smart Onboard
          </button>
          <button className="flex items-center gap-2 bg-primary text-primary-foreground px-4 py-2 rounded-lg text-sm font-medium hover:bg-primary/90 transition-colors">
            <Plus className="w-4 h-4" /> Add Student
          </button>
        </div>
      </div>

      {showSmartOnboard && (
        <div className="bg-card border-2 border-indigo-500/20 rounded-xl p-6 shadow-sm mb-6">
          <div className="flex items-center gap-2 mb-4">
            <div className="w-8 h-8 rounded-full bg-indigo-500/10 flex items-center justify-center">
              <Zap className="w-4 h-4 text-indigo-500 fill-indigo-500" />
            </div>
            <div>
              <h3 className="text-lg font-bold text-foreground">Smart Onboarding</h3>
              <p className="text-xs text-muted-foreground">Quickly generate student seats using Roll Numbers.</p>
            </div>
          </div>
          
          <form onSubmit={handleSmartOnboard} className="space-y-4">
            <div className="grid grid-cols-2 gap-4">
              <div className="space-y-2">
                <label className="text-sm font-medium">Class / Year</label>
                <select 
                  value={selectedClass}
                  onChange={(e) => setSelectedClass(e.target.value)}
                  className="w-full bg-background border border-border rounded-lg px-4 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500/50"
                >
                  <option>10th</option>
                  <option>11th</option>
                  <option>B.Tech 1st Year</option>
                </select>
              </div>
              <div className="space-y-2">
                <label className="text-sm font-medium">Section</label>
                <select 
                  value={selectedSection}
                  onChange={(e) => setSelectedSection(e.target.value)}
                  className="w-full bg-background border border-border rounded-lg px-4 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500/50"
                >
                  <option>A</option>
                  <option>B</option>
                  <option>C</option>
                </select>
              </div>
            </div>
            
            <div className="space-y-2">
              <label className="text-sm font-medium text-foreground">Roll Numbers (Comma Separated)</label>
              <textarea
                required
                value={rollNumbersInput}
                onChange={(e) => setRollNumbersInput(e.target.value)}
                placeholder="e.g. 1, 2, 3, 4, 5  OR  B1, B2, B3"
                className="w-full h-24 bg-background border border-border rounded-lg px-4 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500/50 resize-none font-mono"
              />
            </div>

            <div className="flex justify-end gap-3 pt-2">
              <button 
                type="button" 
                onClick={() => setShowSmartOnboard(false)}
                className="px-4 py-2 text-sm font-medium border rounded-lg hover:bg-secondary/50"
              >
                Cancel
              </button>
              <button 
                type="submit"
                className="px-4 py-2 text-sm font-medium bg-indigo-500 text-white rounded-lg hover:bg-indigo-600 transition-colors"
              >
                Generate Seats
              </button>
            </div>
          </form>
        </div>
      )}

      <div className="bg-card border rounded-xl shadow-sm flex flex-col">
        <div className="p-4 border-b border-border flex flex-col sm:flex-row justify-between gap-4">
          <div className="relative flex-1 max-w-md">
            <Search className="absolute left-3 top-2.5 h-4 w-4 text-muted-foreground" />
            <input 
              type="text" 
              placeholder="Search students by name or roll no..."
              value={search}
              onChange={(e) => setSearch(e.target.value)}
              className="w-full pl-9 pr-4 py-2 bg-background border border-input rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-ring"
            />
          </div>
          <div className="flex gap-2">
            <button className="flex items-center gap-2 bg-background border border-input px-3 py-2 rounded-lg text-sm font-medium hover:bg-secondary transition-colors">
              <Filter className="w-4 h-4" /> Filter
            </button>
            <button className="flex items-center gap-2 bg-background border border-input px-3 py-2 rounded-lg text-sm font-medium hover:bg-secondary transition-colors">
              <Download className="w-4 h-4" /> Export
            </button>
          </div>
        </div>

        <div className="overflow-x-auto">
          <table className="w-full text-left border-collapse">
            <thead>
              <tr className="border-b border-border bg-secondary/20">
                <th className="px-6 py-3 text-xs font-semibold text-muted-foreground uppercase tracking-wider">Roll No.</th>
                <th className="px-6 py-3 text-xs font-semibold text-muted-foreground uppercase tracking-wider">Student Name</th>
                <th className="px-6 py-3 text-xs font-semibold text-muted-foreground uppercase tracking-wider">Class</th>
                <th className="px-6 py-3 text-xs font-semibold text-muted-foreground uppercase tracking-wider">Attendance</th>
                <th className="px-6 py-3 text-xs font-semibold text-muted-foreground uppercase tracking-wider">Status</th>
                <th className="px-6 py-3 text-xs font-semibold text-muted-foreground uppercase tracking-wider text-right">Actions</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-border">
              {students.filter(s => s.name.toLowerCase().includes(search.toLowerCase()) || s.roll.includes(search)).map((student) => (
                <tr key={student.id} className="hover:bg-secondary/30 transition-colors">
                  <td className="px-6 py-4 text-sm font-medium text-muted-foreground">{student.roll}</td>
                  <td className="px-6 py-4">
                    <div className="flex items-center gap-3">
                      <div className="w-8 h-8 rounded-full bg-blue-500/10 text-blue-500 flex items-center justify-center font-bold text-xs">
                        {student.name ? student.name.charAt(0) : <UserPlus className="w-3 h-3" />}
                      </div>
                      <span className={`font-medium ${student.name ? "text-foreground" : "text-indigo-500 italic cursor-pointer hover:underline"}`}>
                        {student.name || "Add Details"}
                      </span>
                    </div>
                  </td>
                  <td className="px-6 py-4 text-sm text-muted-foreground">{student.class}</td>
                  <td className="px-6 py-4 text-sm font-medium">
                    <span className={parseInt(student.attendance) > 80 ? "text-green-500" : "text-red-500"}>
                      {student.attendance}
                    </span>
                  </td>
                  <td className="px-6 py-4">
                    <span className={`px-2.5 py-1 rounded-full text-xs font-medium ${student.status === 'Active' ? 'bg-green-500/10 text-green-500' : 'bg-red-500/10 text-red-500'}`}>
                      {student.status}
                    </span>
                  </td>
                  <td className="px-6 py-4 text-right">
                    <button className="text-muted-foreground hover:text-foreground transition-colors p-1 rounded hover:bg-secondary">
                      <MoreHorizontal className="w-5 h-5" />
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
        <div className="px-6 py-4 border-t border-border flex justify-between items-center text-sm text-muted-foreground">
          <span>Showing 1 to 5 of 5 entries</span>
          <div className="flex gap-2">
            <button className="px-3 py-1 border border-input rounded-md hover:bg-secondary transition-colors disabled:opacity-50" disabled>Previous</button>
            <button className="px-3 py-1 border border-input rounded-md hover:bg-secondary transition-colors disabled:opacity-50" disabled>Next</button>
          </div>
        </div>
      </div>
    </div>
  );
}
