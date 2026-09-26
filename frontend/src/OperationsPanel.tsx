import { useEffect, useState } from "react";
import { api, type Row } from "./api";

export function OperationsPanel() {
  const [report, setReport] = useState<Row | null>(null);
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);
  async function refresh() {
    setLoading(true);
    setError("");
    try { setReport(await api("/operations")); }
    catch { setError("Operational status is unavailable. Check the service and try again."); }
    finally { setLoading(false); }
  }
  useEffect(() => { void refresh(); }, []);
  return <section className="panel spaced" aria-label="Operational status">
    <div className="panel-heading">
      <h2>Service health</h2>
      <button className="button small" onClick={() => void refresh()} disabled={loading}>
        {loading ? "Checking…" : "Check health"}
      </button>
    </div>
    <div className="panel-body" aria-live="polite">
      {error && <p role="alert">{error}</p>}
      {!report && !error && <p>Checking database, evidence storage and worker…</p>}
      {report && <>
        <p><strong>{report.readiness.ready ? "Service is ready" : "Service needs attention"}</strong></p>
        <div className="scroll-table"><table>
          <thead><tr><th>Component</th><th>Current check</th></tr></thead>
          <tbody>{Object.entries(report.readiness.components).map(([key, healthy]) =>
            <tr key={key}><td>{{database: "Database", schema: "Database version", evidence_storage: "Evidence storage", worker: "Worker heartbeat"}[key] || key}</td>
              <td>{healthy ? "Available" : key === "worker" && !report.readiness.worker_required ? "No recent heartbeat · optional in this configuration" : "Unavailable or stale"}</td></tr>)}</tbody>
        </table></div>
        <p>Agency queue: <strong>{report.tenant.jobs.QUEUED || 0}</strong> waiting · <strong>{report.tenant.jobs.RUNNING || 0}</strong> running · <strong>{report.tenant.jobs.FAILED || 0}</strong> failed.</p>
        <p>Oldest waiting job: {report.tenant.oldest_queued_seconds}s. Expired running leases: {report.tenant.expired_running_leases}.</p>
        <p className="muted">These checks describe this installation. They do not verify blockchain provider coverage or SAHYOG connectivity. Job counts are limited to your agency.</p>
      </>}
    </div>
  </section>;
}
