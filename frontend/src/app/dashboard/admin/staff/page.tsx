"use client";

import { useState } from "react";
import { Users, Mail, Plus, ShieldCheck, Search, ShieldAlert } from "lucide-react";

export default function FacultyAccessManagement() {
  const [isAdding, setIsAdding] = useState(false);
  const [email, setEmail] = useState("");
  const [name, setName] = useState("");

  const handleAdd = (e: React.FormEvent) => {
    e.preventDefault();
    setTimeout(() => {
      alert(`Granted Faculty Access to ${email}`);
      setIsAdding(false);
      setEmail("");
      setName("");
    }, 500);
  };

  return (
    <div className="space-y-8 animate-in fade-in slide-in-from-bottom-4 duration-500 max-w-5xl mx-auto">
      <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4">
        <div>
          <h1 className="text-3xl font-bold tracking-tight text-foreground flex items-center gap-2">
            <ShieldCheck className="w-8 h-8 text-indigo-500" /> Faculty Access Management
          </h1>
          <p className="text-muted-foreground mt-2">Authorize emails to grant them login access to the Faculty Portal.</p>
        </div>
        <button 
          onClick={() => setIsAdding(true)}
          className="bg-primary text-primary-foreground text-sm font-medium px-4 py-2 rounded-lg flex items-center gap-2 hover:opacity-90 transition-opacity"
        >
          <Plus className="w-4 h-4" /> Authorize Faculty
        </button>
      </div>

      <div className="bg-yellow-500/10 border border-yellow-500/20 rounded-xl p-4 flex gap-3 text-yellow-600 dark:text-yellow-400">
        <ShieldAlert className="w-5 h-5 shrink-0 mt-0.5" />
        <div className="text-sm font-medium">
          <strong>Strict Access Control:</strong> Only emails authorized on this page will be allowed to log into this institution. Random users attempting to sign in with Google or Email will be rejected.
        </div>
      </div>

      {isAdding && (
        <div className="bg-card border rounded-xl p-6 shadow-sm">
          <h3 className="text-lg font-medium mb-4">Grant Access</h3>
          <form onSubmit={handleAdd} className="space-y-4">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div className="space-y-2">
                <label className="text-sm font-medium text-foreground">Email Address</label>
                <div className="relative">
                  <Mail className="absolute left-3 top-2.5 h-5 w-5 text-muted-foreground" />
                  <input
                    type="email"
                    required
                    value={email}
                    onChange={(e) => setEmail(e.target.value)}
                    className="w-full bg-background border border-border rounded-lg pl-10 pr-4 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-primary/50"
                    placeholder="teacher@school.edu"
                  />
                </div>
              </div>
              <div className="space-y-2">
                <label className="text-sm font-medium text-foreground">Name (Optional)</label>
                <div className="relative">
                  <Users className="absolute left-3 top-2.5 h-5 w-5 text-muted-foreground" />
                  <input
                    type="text"
                    value={name}
                    onChange={(e) => setName(e.target.value)}
                    className="w-full bg-background border border-border rounded-lg pl-10 pr-4 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-primary/50"
                    placeholder="John Doe"
                  />
                </div>
              </div>
            </div>

            <div className="flex justify-end gap-3 pt-4 border-t border-border mt-4">
              <button 
                type="button" 
                onClick={() => setIsAdding(false)}
                className="px-4 py-2 text-sm font-medium border rounded-lg hover:bg-secondary/50"
              >
                Cancel
              </button>
              <button 
                type="submit"
                className="px-4 py-2 text-sm font-medium bg-primary text-primary-foreground rounded-lg hover:opacity-90"
              >
                Save & Invite
              </button>
            </div>
          </form>
        </div>
      )}

      {/* Existing Faculty List */}
      <div className="bg-card border rounded-xl shadow-sm overflow-hidden flex flex-col">
        <div className="p-4 border-b border-border flex flex-col sm:flex-row justify-between gap-4">
          <div className="relative flex-1 max-w-md">
            <Search className="absolute left-3 top-2.5 h-4 w-4 text-muted-foreground" />
            <input 
              type="text" 
              placeholder="Search authorized emails..."
              className="w-full pl-9 pr-4 py-2 bg-background border border-input rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-ring"
            />
          </div>
        </div>
        <table className="w-full text-left text-sm">
          <thead className="bg-secondary/50 border-b">
            <tr>
              <th className="px-6 py-3 font-medium text-muted-foreground">Email</th>
              <th className="px-6 py-3 font-medium text-muted-foreground">Name</th>
              <th className="px-6 py-3 font-medium text-muted-foreground">Status</th>
              <th className="px-6 py-3 font-medium text-muted-foreground text-right">Actions</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-border">
            <tr className="hover:bg-secondary/20 transition-colors">
              <td className="px-6 py-4 font-medium text-foreground">math.teacher@school.edu</td>
              <td className="px-6 py-4 text-muted-foreground">Alan Turing</td>
              <td className="px-6 py-4">
                <span className="bg-green-500/10 text-green-500 px-2 py-1 rounded text-xs font-medium">Logged In Recently</span>
              </td>
              <td className="px-6 py-4 text-right">
                <button className="text-red-500 hover:text-red-600 text-sm font-medium">Revoke</button>
              </td>
            </tr>
            <tr className="hover:bg-secondary/20 transition-colors">
              <td className="px-6 py-4 font-medium text-foreground">physics@school.edu</td>
              <td className="px-6 py-4 text-muted-foreground"><span className="italic text-muted-foreground/70">Not specified</span></td>
              <td className="px-6 py-4">
                <span className="bg-yellow-500/10 text-yellow-500 px-2 py-1 rounded text-xs font-medium">Invite Sent</span>
              </td>
              <td className="px-6 py-4 text-right">
                <button className="text-red-500 hover:text-red-600 text-sm font-medium">Revoke</button>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>
  );
}
