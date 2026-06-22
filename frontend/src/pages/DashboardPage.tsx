import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { Navbar } from "../components/Navbar";
import { Card } from "../components/Card";
import { Button } from "../components/Button";
import { api, extractErrorMessage } from "../lib/api";
import type { DashboardData } from "../lib/types";

export function DashboardPage() {
  const [data, setData] = useState<DashboardData | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    api.dashboard
      .get()
      .then(setData)
      .catch((err) => setError(extractErrorMessage(err)))
      .finally(() => setIsLoading(false));
  }, []);

  return (
    <div className="min-h-screen flex flex-col">
      <Navbar />
      <div className="container-page py-12 flex-1">
        <div className="flex items-center justify-between mb-8">
          <h1 className="font-display text-3xl font-medium text-ink">Dashboard</h1>
          <Link to="/analyze">
            <Button variant="primary">New analysis</Button>
          </Link>
        </div>

        {isLoading && <p className="text-slate text-sm">Loading your dashboard…</p>}

        {error && (
          <div role="alert" className="text-sm text-gap bg-gap-dim border border-gap/20 rounded px-4 py-3 mb-6">
            {error}
          </div>
        )}

        {data && (
          <>
            <div className="grid sm:grid-cols-2 lg:grid-cols-4 gap-4 mb-8">
              <StatCard label="Resumes" value={data.resume_count} />
              <StatCard label="Job descriptions" value={data.job_description_count} />
              <StatCard label="Analyses run" value={data.analysis_count} />
              <StatCard
                label="Latest score"
                value={data.latest_score !== null ? Math.round(data.latest_score) : "—"}
              />
            </div>

            {data.analysis_count === 0 ? (
              <Card className="p-10 text-center">
                <h2 className="font-display text-xl font-medium text-ink">No analyses yet</h2>
                <p className="mt-2 text-sm text-slate max-w-sm mx-auto">
                  Upload a resume and a job description to get your first ATS score and
                  recruiter feedback.
                </p>
                <Link to="/analyze" className="inline-block mt-6">
                  <Button variant="primary">Start your first analysis</Button>
                </Link>
              </Card>
            ) : (
              <Card className="p-6">
                <h2 className="font-semibold text-ink mb-4">Recent analyses</h2>
                <div className="flex flex-col divide-y divide-line">
                  {data.recent_analyses.map((a) => (
                    <div key={a.id} className="py-3 flex items-center justify-between text-sm">
                      <span className="text-slate">
                        {new Date(a.created_at).toLocaleDateString()}
                      </span>
                      <span className="font-mono font-medium text-ink">
                        {Math.round(a.overall_score)}/100
                      </span>
                    </div>
                  ))}
                </div>
              </Card>
            )}
          </>
        )}
      </div>
    </div>
  );
}

function StatCard({ label, value }: { label: string; value: number | string }) {
  return (
    <Card className="p-5">
      <div className="font-mono text-2xl font-semibold text-ink">{value}</div>
      <div className="text-sm text-slate mt-1">{label}</div>
    </Card>
  );
}
