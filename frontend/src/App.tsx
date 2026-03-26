import { useState, useEffect, useCallback, useMemo } from 'react';
import { Plus, Trash2, X, Activity } from 'lucide-react';
import { CameraStats } from './types';

function App() {
  const [cameras, setCameras] = useState<CameraStats[]>([]);
  const [selectedCameraId, setSelectedCameraId] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);
  const [lastRefresh, setLastRefresh] = useState<Date>(new Date());
  const [countdown, setCountdown] = useState(30);
  const [imgKey, setImgKey] = useState(0);
  const [showAddModal, setShowAddModal] = useState(false);
  const [newCam, setNewCam] = useState({ id: '', name: '', rsu: '', x: '0', y: '0', lat: '51.5', lon: '-0.1' });

  const selectedCamera = useMemo(() => {
    return cameras.find(c => c.camera_id === selectedCameraId) || cameras[0] || null;
  }, [cameras, selectedCameraId]);

  useEffect(() => {
    if (cameras.length > 0 && !selectedCameraId) {
      setSelectedCameraId(cameras[0].camera_id);
    }
  }, [cameras, selectedCameraId]);

  const fetchCameras = useCallback(async () => {
    try {
      const response = await fetch('/api/cameras/');
      if (!response.ok) throw new Error('API unstable');
      const data = await response.json();
      setCameras(data);
      setLastRefresh(new Date());
      setCountdown(30);
      setImgKey(prev => prev + 1);
    } catch (error) {
      console.error('Error fetching cameras:', error);
    } finally {
      setLoading(false);
    }
  }, []);

  const handleAddCamera = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      const response = await fetch('/api/cameras/', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          camera_id: newCam.id,
          name: newCam.name,
          rsu_id: newCam.rsu,
          x: parseFloat(newCam.x),
          y: parseFloat(newCam.y),
          lat: parseFloat(newCam.lat),
          lon: parseFloat(newCam.lon)
        })
      });
      if (response.ok) {
        setShowAddModal(false);
        fetchCameras();
        setSelectedCameraId(newCam.id);
      }
    } catch (error) {
      console.error('Error adding camera:', error);
    }
  };

  const handleDeleteCamera = async (id: string, e: React.MouseEvent) => {
    e.stopPropagation();
    if (!confirm(`Delete camera ${id}?`)) return;
    try {
      const response = await fetch(`/api/cameras/${id}`, { method: 'DELETE' });
      if (response.ok) {
        fetchCameras();
        if (selectedCameraId === id) setSelectedCameraId(null);
      }
    } catch (error) {
      console.error('Error deleting camera:', error);
    }
  };

  useEffect(() => {
    fetchCameras();
    const interval = setInterval(fetchCameras, 30000);
    return () => clearInterval(interval);
  }, [fetchCameras]);

  useEffect(() => {
    const timer = setInterval(() => {
      setCountdown((prev) => (prev > 0 ? prev - 1 : 30));
    }, 1000);
    return () => clearInterval(timer);
  }, []);

  const formatId = (id: string) => id.replace('JamCam_', '').replace('JamCams_', '');
  const totalDetections = cameras.reduce((s, c) => s + c.total_detections, 0);

  return (
    <div className="shell">
      {/* ═══ TOP BAR ═══ */}
      <div className="topbar">
        <div className="topbar-brand">
          <h1>TrafficVision</h1>
          <span className="separator" />
          <span className="version">CMD CENTER v1.0</span>
        </div>
        <div className="topbar-meta">
          <div className="meta-item">
            <span className="meta-dot" />
            <span>SYSTEM ONLINE</span>
          </div>
          <span style={{ color: 'var(--text-tertiary)' }}>│</span>
          <div className="meta-item">
            <span>{lastRefresh.toLocaleTimeString('en-GB', { hour12: false })}</span>
          </div>
          <span style={{ color: 'var(--text-tertiary)' }}>│</span>
          <div className="meta-item">
            <span style={{ color: 'var(--amber)' }}>T-{String(countdown).padStart(2, '0')}s</span>
          </div>
        </div>
      </div>

      {/* ═══ MAIN ═══ */}
      <div className="main-content">

        {/* ─── SIDEBAR ─── */}
        <aside className="sidebar">
          <div className="sidebar-header">
            <span>NODES <span className="cam-count">({cameras.length})</span></span>
            <button className="btn-add" onClick={() => setShowAddModal(true)} title="Register Node">
              <Plus size={14} />
            </button>
          </div>
          <div className="camera-list">
            {loading && cameras.length === 0 ? (
              <div style={{ padding: '24px 16px', color: 'var(--text-tertiary)', fontFamily: 'var(--font-mono)', fontSize: '0.75rem' }}>
                LOADING NODES...
              </div>
            ) : cameras.length === 0 ? (
              <div style={{ padding: '24px 16px', color: 'var(--text-tertiary)', fontFamily: 'var(--font-mono)', fontSize: '0.75rem' }}>
                NO NODES REGISTERED
              </div>
            ) : (
              cameras.map((cam, i) => (
                <div
                  key={cam.camera_id}
                  className={`cam-card ${selectedCamera?.camera_id === cam.camera_id ? 'active' : ''}`}
                  onClick={() => setSelectedCameraId(cam.camera_id)}
                  style={{ animationDelay: `${i * 40}ms` }}
                >
                  <div className="cam-card-row">
                    <span className="cam-id">{cam.name || formatId(cam.camera_id)}</span>
                    <div style={{ display: 'flex', gap: '6px', alignItems: 'center' }}>
                      {cam.rsu_id && <span className="cam-badge">{cam.rsu_id}</span>}
                      <button className="btn-delete" onClick={(e) => handleDeleteCamera(cam.camera_id, e)} title="Delete">
                        <Trash2 size={12} />
                      </button>
                    </div>
                  </div>
                  <div className="cam-stats-row">
                    <span>DET <span className="stat-val">{cam.total_detections}</span></span>
                    <span>
                      <Activity size={10} style={{ verticalAlign: 'middle', marginRight: '2px' }} />
                      <span className="stat-live">{cam.vehicle_count_30s}</span>
                      <span style={{ marginLeft: '2px' }}>/30s</span>
                    </span>
                  </div>
                </div>
              ))
            )}
          </div>
        </aside>

        {/* ─── MAIN PANEL ─── */}
        <div className="main-panel">
          {selectedCamera ? (
            <>
              {/* ─ Feed ─ */}
              <div className="feed-container">
                {/* HUD Corners */}
                <div className="hud-overlay">
                  <div className="hud-corner-tr" />
                  <div className="hud-corner-bl" />
                </div>

                {/* LIVE badge */}
                <div className="live-badge">
                  <span className="live-dot" />
                  LIVE
                </div>

                {/* Camera ID stamp */}
                <div className="hud-cam-id">
                  NODE:{selectedCamera.name || formatId(selectedCamera.camera_id)}
                  {selectedCamera.rsu_id && ` // RSU:${selectedCamera.rsu_id}`}
                </div>

                {selectedCamera.image_url ? (
                  <img
                    key={`${selectedCamera.camera_id}-${imgKey}`}
                    src={`${selectedCamera.image_url}${selectedCamera.image_url.includes('?') ? '&' : '?'}t=${Date.now()}`}
                    alt={`Live feed — ${selectedCamera.camera_id}`}
                    onLoad={(e) => (e.currentTarget.style.opacity = '1')}
                    style={{ opacity: 0, transition: 'opacity 0.5s ease-in-out' }}
                  />
                ) : (
                  <div className="feed-placeholder">
                    <div className="spinner-ring" />
                    <span>AWAITING FEED</span>
                    <span style={{ fontSize: '0.65rem', color: 'var(--text-tertiary)' }}>
                      {selectedCamera.rsu_id ? `RSU:${selectedCamera.rsu_id}` : `ID:${formatId(selectedCamera.camera_id)}`}
                    </span>
                  </div>
                )}
              </div>

              {/* ─ Data Strip ─ */}
              <div className="data-strip">
                <div className="data-cell">
                  <span className="data-label">Location</span>
                  <span className="data-value val-amber">{selectedCamera.name || formatId(selectedCamera.camera_id)}</span>
                </div>
                <div className="data-cell">
                  <span className="data-label">Coordinates</span>
                  <span className="data-value">{selectedCamera.lat.toFixed(4)}, {selectedCamera.lon.toFixed(4)}</span>
                </div>
                <div className="data-cell">
                  <span className="data-label">Flow / 30s</span>
                  <span className="data-value val-green">{selectedCamera.vehicle_count_30s}</span>
                </div>
                <div className="data-cell">
                  <span className="data-label">Total Detections</span>
                  <span className="data-value">{selectedCamera.total_detections}</span>
                </div>
                <div className="data-cell">
                  <span className="data-label">All Nodes Total</span>
                  <span className="data-value val-cyan">{totalDetections}</span>
                </div>
              </div>
            </>
          ) : (
            <div className="empty-panel">
              ← SELECT A NODE TO VIEW FEED
            </div>
          )}
        </div>
      </div>

      {/* ═══ MODAL ═══ */}
      {showAddModal && (
        <div className="modal-overlay" onClick={() => setShowAddModal(false)}>
          <div className="modal-panel" onClick={(e) => e.stopPropagation()}>
            <div className="modal-header">
              <span>Register Node</span>
              <button onClick={() => setShowAddModal(false)}><X size={16} /></button>
            </div>
            <div className="modal-body">
              <form onSubmit={handleAddCamera}>
                <div className="form-grid">
                  <div className="form-group">
                    <label>Camera ID</label>
                    <input value={newCam.id} onChange={e => setNewCam({ ...newCam, id: e.target.value })} placeholder="CAM_001" required />
                  </div>
                  <div className="form-group">
                    <label>RSU ID</label>
                    <input value={newCam.rsu} onChange={e => setNewCam({ ...newCam, rsu: e.target.value })} placeholder="ZONE-A-1" required />
                  </div>
                  <div className="form-group">
                    <label>Sim X</label>
                    <input type="number" step="any" value={newCam.x} onChange={e => setNewCam({ ...newCam, x: e.target.value })} required />
                  </div>
                  <div className="form-group">
                    <label>Sim Y</label>
                    <input type="number" step="any" value={newCam.y} onChange={e => setNewCam({ ...newCam, y: e.target.value })} required />
                  </div>
                  <div className="form-group">
                    <label>Latitude</label>
                    <input type="number" step="any" value={newCam.lat} onChange={e => setNewCam({ ...newCam, lat: e.target.value })} required />
                  </div>
                  <div className="form-group">
                    <label>Longitude</label>
                    <input type="number" step="any" value={newCam.lon} onChange={e => setNewCam({ ...newCam, lon: e.target.value })} required />
                  </div>
                </div>
                <button type="submit" className="btn-submit">Register Node</button>
              </form>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

export default App;
