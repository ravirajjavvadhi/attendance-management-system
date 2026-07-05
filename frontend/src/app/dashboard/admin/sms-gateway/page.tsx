"use client";

import { useState, useEffect } from "react";
import { useSession } from "next-auth/react";
import { 
  Smartphone, Wifi, WifiOff, Battery, BatteryCharging, 
  MessageSquare, CheckCircle2, XCircle, RefreshCw, Plus, Trash2,
  Settings, Edit2, Shield, AlertTriangle
} from "lucide-react";

export default function SmsGatewayPage() {
  const { data: session } = useSession();
  const token = (session as any)?.accessToken;
  
  const [devices, setDevices] = useState([]);
  const [settings, setSettings] = useState<any>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [isGenerating, setIsGenerating] = useState(false);
  const [pairingToken, setPairingToken] = useState("");
  const [stats, setStats] = useState({ sent_today: 0, failed_today: 0, queue_size: 0 });

  const fetchDevices = async () => {
    if (!token) return;
    try {
      const baseUrl = (process.env.NEXT_PUBLIC_API_URL || "").replace(/\/$/, "");
      
      const res = await fetch(`${baseUrl}/api/v1/device`, {
        headers: { Authorization: `Bearer ${token}` }
      });
      if (res.ok) {
        setDevices(await res.json());
      }
      
      const statsRes = await fetch(`${baseUrl}/api/v1/sms/stats`, {
        headers: { Authorization: `Bearer ${token}` }
      });
      if (statsRes.ok) {
        setStats(await statsRes.json());
      }
      
      const settingsRes = await fetch(`${baseUrl}/api/v1/institution/me/settings`, {
        headers: { Authorization: `Bearer ${token}` }
      });
      if (settingsRes.ok) {
        setSettings(await settingsRes.json());
      }
      
    } catch (error) {
      console.error("Failed to fetch data", error);
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    fetchDevices();
    const interval = setInterval(fetchDevices, 15000);
    return () => clearInterval(interval);
  }, [token]);

  const generateToken = async () => {
    if (!token) return;
    setIsGenerating(true);
    try {
      const baseUrl = (process.env.NEXT_PUBLIC_API_URL || "").replace(/\/$/, "");
      const res = await fetch(`${baseUrl}/api/v1/device/generate-token`, {
        method: "POST",
        headers: { Authorization: `Bearer ${token}`, "Content-Type": "application/json" },
        body: JSON.stringify({ device_name: "New Gateway Device" })
      });
      if (res.ok) {
        const data = await res.json();
        setPairingToken(data.pairing_token);
        fetchDevices();
      }
    } finally {
      setIsGenerating(false);
    }
  };

  const removeDevice = async (id: number) => {
    if (!token) return;
    if (!confirm("Are you sure you want to archive this device?")) return;
    const baseUrl = (process.env.NEXT_PUBLIC_API_URL || "").replace(/\/$/, "");
    await fetch(`${baseUrl}/api/v1/device/${id}`, {
      method: "DELETE",
      headers: { Authorization: `Bearer ${token}` }
    });
    fetchDevices();
  };

  const renameDevice = async (id: number, currentName: string) => {
    if (!token) return;
    const newName = prompt("Enter new device name:", currentName);
    if (!newName || newName === currentName) return;
    
    const baseUrl = (process.env.NEXT_PUBLIC_API_URL || "").replace(/\/$/, "");
    await fetch(`${baseUrl}/api/v1/device/${id}`, {
      method: "PATCH",
      headers: { Authorization: `Bearer ${token}`, "Content-Type": "application/json" },
      body: JSON.stringify({ device_name: newName })
    });
    fetchDevices();
  };

  const toggleEngine = async () => {
    if (!token || !settings) return;
    const newEngine = settings.sms_engine === "ENTERPRISE" ? "LEGACY" : "ENTERPRISE";
    if (!confirm(`Switch SMS Engine to ${newEngine}?`)) return;
    
    const baseUrl = (process.env.NEXT_PUBLIC_API_URL || "").replace(/\/$/, "");
    await fetch(`${baseUrl}/api/v1/institution/me/settings`, {
      method: "PATCH",
      headers: { Authorization: `Bearer ${token}`, "Content-Type": "application/json" },
      body: JSON.stringify({ sms_engine: newEngine })
    });
    fetchDevices();
  };

  return (
    <div className="space-y-8 animate-in fade-in slide-in-from-bottom-4 duration-500">
      <div className="flex justify-between items-end">
        <div>
          <h1 className="text-3xl font-bold tracking-tight text-foreground flex items-center gap-3">
            SMS Gateway
            {settings?.sms_engine === "ENTERPRISE" && (
              <span className="bg-primary/10 text-primary text-xs px-2 py-1 rounded flex items-center gap-1 border border-primary/20">
                <Shield className="w-3 h-3" /> Enterprise Engine Active
              </span>
            )}
          </h1>
          <p className="text-muted-foreground mt-1">Manage Android devices paired to your institution for native SMS delivery.</p>
        </div>
        <button 
          onClick={generateToken}
          disabled={isGenerating}
          className="bg-primary text-primary-foreground hover:bg-primary/90 h-10 px-4 py-2 rounded-lg font-medium text-sm transition-colors flex items-center gap-2 disabled:opacity-50"
        >
          {isGenerating ? <RefreshCw className="w-4 h-4 animate-spin" /> : <Plus className="w-4 h-4" />}
          Pair New Device
        </button>
      </div>

      {pairingToken && (
        <div className="bg-primary/10 border border-primary/20 rounded-xl p-6 flex flex-col items-center justify-center space-y-4">
          <p className="text-sm font-medium text-primary">Enter this 6-digit pairing code in the EduFlow SMS Gateway App:</p>
          <div className="text-4xl font-black tracking-[0.5em] text-foreground">{pairingToken}</div>
          <button onClick={() => setPairingToken("")} className="text-sm text-muted-foreground hover:underline">Close</button>
        </div>
      )}

      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <div className="col-span-2 space-y-6">
          <div className="bg-card border rounded-xl shadow-sm overflow-hidden flex flex-col">
            <div className="px-6 py-5 border-b border-border flex justify-between items-center bg-muted/30">
              <h2 className="text-lg font-semibold flex items-center gap-2">
                <Smartphone className="w-5 h-5 text-primary" />
                Connected Devices
              </h2>
            </div>
            <div className="divide-y divide-border">
              {isLoading ? (
                <div className="px-6 py-8 text-center text-muted-foreground">Loading devices...</div>
              ) : devices.length === 0 ? (
                <div className="px-6 py-8 text-center text-muted-foreground flex flex-col items-center gap-2">
                  <WifiOff className="w-8 h-8 text-muted-foreground/50" />
                  <p>No devices connected yet.</p>
                </div>
              ) : (
                devices.map((device: any) => {
                  const isOnline = device.status === "ONLINE";
                  const lastSeen = device.last_seen ? new Date(device.last_seen).toLocaleTimeString() : "Never";
                  
                  return (
                    <div key={device.id} className="p-6 flex flex-col sm:flex-row sm:items-center justify-between gap-4">
                      <div className="flex items-start gap-4">
                        <div className={`w-12 h-12 rounded-xl flex items-center justify-center shrink-0 ${isOnline ? 'bg-green-500/10 text-green-500' : 'bg-secondary text-muted-foreground'}`}>
                          {isOnline ? <Wifi className="w-6 h-6" /> : <WifiOff className="w-6 h-6" />}
                        </div>
                        <div>
                          <h3 className="font-semibold text-foreground flex items-center gap-2">
                            {device.device_name}
                            <button onClick={() => renameDevice(device.id, device.device_name)} className="text-muted-foreground hover:text-foreground">
                              <Edit2 className="w-3 h-3" />
                            </button>
                            {isOnline && <span className="w-2 h-2 rounded-full bg-green-500 animate-pulse"></span>}
                          </h3>
                          <div className="flex items-center gap-3 text-xs text-muted-foreground mt-1">
                            {device.pairing_token ? (
                              <span className="text-orange-500 font-medium">Waiting for app to pair... (Code: {device.pairing_token})</span>
                            ) : (
                              <>
                                <span>ID: {device.id}</span>
                                <span>•</span>
                                <span>Last seen: {lastSeen}</span>
                              </>
                            )}
                          </div>
                          
                          {/* Enhanced Health Metrics */}
                          {isOnline && !device.pairing_token && device.network_type && (
                            <div className="flex flex-wrap gap-2 mt-2">
                              <span className="px-2 py-0.5 bg-muted text-xs rounded border text-muted-foreground">App: v{device.app_version || 'Unknown'}</span>
                              <span className="px-2 py-0.5 bg-muted text-xs rounded border text-muted-foreground">RAM: {device.ram_usage || '?'}</span>
                              <span className="px-2 py-0.5 bg-muted text-xs rounded border text-muted-foreground">Storage: {device.storage_remaining || '?'}</span>
                            </div>
                          )}
                        </div>
                      </div>
                      
                      {!device.pairing_token && (
                        <div className="flex items-center gap-4 bg-secondary/30 px-4 py-2 rounded-lg border">
                          <div className="flex flex-col items-center">
                            <span className="text-[10px] text-muted-foreground uppercase tracking-wider mb-1">Battery</span>
                            <div className="flex items-center gap-1 font-medium text-sm">
                              {device.battery_percentage !== null ? (
                                <>
                                  {device.battery_percentage}% 
                                  {device.is_charging ? <BatteryCharging className="w-4 h-4 text-green-500" /> : <Battery className="w-4 h-4 text-muted-foreground" />}
                                </>
                              ) : "-"}
                            </div>
                          </div>
                          <div className="w-px h-8 bg-border"></div>
                          <div className="flex flex-col items-center">
                            <span className="text-[10px] text-muted-foreground uppercase tracking-wider mb-1">Network</span>
                            <div className="flex items-center gap-1 font-medium text-sm">
                              {device.network_type || device.sim_operator || "Unknown"} ({device.signal_strength}%)
                            </div>
                          </div>
                        </div>
                      )}
                      
                      <button 
                        onClick={() => removeDevice(device.id)}
                        className="p-2 text-muted-foreground hover:bg-red-500/10 hover:text-red-500 rounded-lg transition-colors"
                      >
                        <Trash2 className="w-4 h-4" />
                      </button>
                    </div>
                  );
                })
              )}
            </div>
          </div>
        </div>

        <div className="space-y-6">
          <div className="bg-card border rounded-xl shadow-sm p-6">
            <h2 className="text-lg font-semibold mb-4 flex items-center gap-2">
              <MessageSquare className="w-5 h-5 text-primary" />
              Live SMS Analytics
            </h2>
            <div className="space-y-4">
              <div className="flex justify-between items-center p-3 bg-secondary/50 rounded-lg">
                <span className="text-sm font-medium text-muted-foreground">Queue Size</span>
                <span className="text-lg font-bold text-foreground">{stats.queue_size}</span>
              </div>
              <div className="flex justify-between items-center p-3 bg-green-500/5 text-green-600 rounded-lg border border-green-500/10">
                <span className="text-sm font-medium flex items-center gap-2"><CheckCircle2 className="w-4 h-4" /> Sent Today</span>
                <span className="text-lg font-bold">{stats.sent_today}</span>
              </div>
              <div className="flex justify-between items-center p-3 bg-red-500/5 text-red-600 rounded-lg border border-red-500/10">
                <span className="text-sm font-medium flex items-center gap-2"><XCircle className="w-4 h-4" /> Failed</span>
                <span className="text-lg font-bold">{stats.failed_today}</span>
              </div>
            </div>
          </div>
          
          <div className="bg-card border rounded-xl shadow-sm p-6">
            <h2 className="text-lg font-semibold mb-4 flex items-center gap-2">
              <Settings className="w-5 h-5 text-muted-foreground" />
              Engine Configuration
            </h2>
            <div className="space-y-4">
              <div className="p-4 bg-muted/40 rounded-lg border border-border">
                <div className="flex justify-between items-center mb-2">
                  <span className="text-sm font-medium">Daily Device Quota</span>
                  <span className="text-sm font-bold">{settings?.max_sms_per_device_per_day || 70} SMS</span>
                </div>
                <p className="text-xs text-muted-foreground">Max messages one device can send per day to prevent carrier bans.</p>
              </div>
              
              <div className="p-4 bg-muted/40 rounded-lg border border-border">
                <div className="flex justify-between items-center mb-2">
                  <span className="text-sm font-medium">Enterprise Queue</span>
                  <button 
                    onClick={toggleEngine}
                    className={`w-10 h-5 rounded-full relative transition-colors ${settings?.sms_engine === "ENTERPRISE" ? "bg-primary" : "bg-muted-foreground/30"}`}
                  >
                    <div className={`w-3 h-3 bg-white rounded-full absolute top-1 transition-transform ${settings?.sms_engine === "ENTERPRISE" ? "left-6" : "left-1"}`}></div>
                  </button>
                </div>
                <p className="text-xs text-muted-foreground">Enable strict atomic locking, UUID idempotency, and ACK guarantees.</p>
              </div>
            </div>
          </div>
          
        </div>
      </div>
    </div>
  );
}
