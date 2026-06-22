"use client";

import { useState } from "react";
import { Building2, Mail, Plus, ShieldCheck } from "lucide-react";

export default function SuperAdminDashboard() {
  const [isCreating, setIsCreating] = useState(false);
  const [institutionName, setInstitutionName] = useState("");
  const [managementEmail, setManagementEmail] = useState("");

  const handleCreate = (e: React.FormEvent) => {
    e.preventDefault();
    // Simulate API call
    setTimeout(() => {
      alert(`Created ${institutionName} and sent invitation to ${managementEmail}`);
      setIsCreating(false);
      setInstitutionName("");
      setManagementEmail("");
    }, 1000);
  };

  return (
    <div className="space-y-8 animate-in fade-in slide-in-from-bottom-4 duration-500 max-w-4xl">
      <div>
        <h1 className="text-3xl font-bold tracking-tight text-foreground flex items-center gap-2">
          <ShieldCheck className="w-8 h-8 text-indigo-500" /> Super Admin
        </h1>
        <p className="text-muted-foreground mt-2">Manage all SaaS tenants and institutions.</p>
      </div>

      <div className="flex items-center justify-between">
        <h2 className="text-xl font-semibold">Institutions</h2>
        <button 
          onClick={() => setIsCreating(true)}
          className="bg-primary text-primary-foreground text-sm font-medium px-4 py-2 rounded-lg flex items-center gap-2 hover:opacity-90 transition-opacity"
        >
          <Plus className="w-4 h-4" /> New Institution
        </button>
      </div>

      {isCreating && (
        <div className="bg-card border rounded-xl p-6 shadow-sm">
          <h3 className="text-lg font-medium mb-4">Provision New Tenant</h3>
          <form onSubmit={handleCreate} className="space-y-4">
            <div className="space-y-2">
              <label className="text-sm font-medium text-foreground">Institution Name</label>
              <div className="relative">
                <Building2 className="absolute left-3 top-2.5 h-5 w-5 text-muted-foreground" />
                <input
                  type="text"
                  required
                  value={institutionName}
                  onChange={(e) => setInstitutionName(e.target.value)}
                  className="w-full bg-background border border-border rounded-lg pl-10 pr-4 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-primary/50"
                  placeholder="e.g. Stanford University"
                />
              </div>
            </div>
            
            <div className="space-y-2">
              <label className="text-sm font-medium text-foreground">Management Email</label>
              <div className="relative">
                <Mail className="absolute left-3 top-2.5 h-5 w-5 text-muted-foreground" />
                <input
                  type="email"
                  required
                  value={managementEmail}
                  onChange={(e) => setManagementEmail(e.target.value)}
                  className="w-full bg-background border border-border rounded-lg pl-10 pr-4 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-primary/50"
                  placeholder="principal@stanford.edu"
                />
              </div>
              <p className="text-xs text-muted-foreground">This email will receive Admin access to setup the institution.</p>
            </div>

            <div className="flex justify-end gap-3 pt-4">
              <button 
                type="button" 
                onClick={() => setIsCreating(false)}
                className="px-4 py-2 text-sm font-medium border rounded-lg hover:bg-secondary/50"
              >
                Cancel
              </button>
              <button 
                type="submit"
                className="px-4 py-2 text-sm font-medium bg-primary text-primary-foreground rounded-lg hover:opacity-90"
              >
                Provision & Invite
              </button>
            </div>
          </form>
        </div>
      )}

      {/* Existing Tenants List */}
      <div className="bg-card border rounded-xl shadow-sm overflow-hidden">
        <table className="w-full text-left text-sm">
          <thead className="bg-secondary/50 border-b">
            <tr>
              <th className="px-6 py-3 font-medium text-muted-foreground">Institution</th>
              <th className="px-6 py-3 font-medium text-muted-foreground">Management Email</th>
              <th className="px-6 py-3 font-medium text-muted-foreground">Status</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-border">
            <tr className="hover:bg-secondary/20 transition-colors">
              <td className="px-6 py-4 font-medium text-foreground">Harvard Business School</td>
              <td className="px-6 py-4 text-muted-foreground">admin@hbs.edu</td>
              <td className="px-6 py-4">
                <span className="bg-green-500/10 text-green-500 px-2 py-1 rounded text-xs font-medium">Active</span>
              </td>
            </tr>
            <tr className="hover:bg-secondary/20 transition-colors">
              <td className="px-6 py-4 font-medium text-foreground">MIT Engineering</td>
              <td className="px-6 py-4 text-muted-foreground">principal@mit.edu</td>
              <td className="px-6 py-4">
                <span className="bg-green-500/10 text-green-500 px-2 py-1 rounded text-xs font-medium">Active</span>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>
  );
}
