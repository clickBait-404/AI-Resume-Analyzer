import { useEffect, useState } from "react";
import type { ReactNode } from "react";
import { Link, useNavigate } from "react-router-dom";

import { Navbar } from "../components/Navbar";
import { Card } from "../components/Card";
import { Button } from "../components/Button";

import { api, extractErrorMessage } from "../lib/api";
import type { DashboardData } from "../lib/types";

import {
  FileText,
  Briefcase,
  BarChart3,
  TrendingUp,
  ArrowUpRight,
} from "lucide-react";

export function DashboardPage() {
  const navigate = useNavigate();

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
        {/* Header */}
        <div className="flex flex-col lg:flex-row lg:items-center lg:justify-between gap-6 mb-10">
          <div>
            <p className="text-sm font-medium text-blue-600 mb-2">
              Resume Analytics
            </p>

            <h1 className="text-4xl font-bold tracking-tight text-slate-900">
              Dashboard
            </h1>

            <p className="mt-2 text-slate-500">
              Track ATS performance and recruiter readiness.
            </p>
          </div>

          <Link to="/analyze">
            <Button variant="primary">
              New Analysis
            </Button>
          </Link>
        </div>

        {/* Loading */}
        {isLoading && (
          <p className="text-slate-500 text-sm">
            Loading your dashboard...
          </p>
        )}

        {/* Error */}
        {error && (
          <div
            role="alert"
            className="
              text-sm
              text-red-700
              bg-red-50
              border
              border-red-200
              rounded-xl
              px-4
              py-3
              mb-6
            "
          >
            {error}
          </div>
        )}

        {/* Dashboard Content */}
        {data && (
          <>
            {/* Stats */}
            <div className="grid md:grid-cols-2 xl:grid-cols-4 gap-6 mb-10">
              <StatCard
                icon={<FileText size={20} />}
                label="Resumes"
                value={data.resume_count}
              />

              <StatCard
                icon={<Briefcase size={20} />}
                label="Job Descriptions"
                value={data.job_description_count}
              />

              <StatCard
                icon={<BarChart3 size={20} />}
                label="Analyses"
                value={data.analysis_count}
              />

              <StatCard
                icon={<TrendingUp size={20} />}
                label="Latest Score"
                value={
                  data.latest_score !== null
                    ? Math.round(data.latest_score)
                    : "—"
                }
              />
            </div>

            {data.analysis_count === 0 ? (
              <Card className="p-12 text-center">
                <h2 className="text-2xl font-bold text-slate-900">
                  No analyses yet
                </h2>

                <p className="mt-3 text-slate-500 max-w-md mx-auto">
                  Upload a resume and a job description to
                  generate your first ATS score and recruiter
                  feedback report.
                </p>

                <Link to="/analyze" className="inline-block mt-6">
                  <Button variant="primary">
                    Start First Analysis
                  </Button>
                </Link>
              </Card>
            ) : (
              <div className="grid lg:grid-cols-3 gap-6">
                {/* Recent Analyses */}
                <Card className="lg:col-span-2 p-8">
                  <div className="flex items-center justify-between mb-6">
                    <h2 className="text-xl font-semibold text-slate-900">
                      Recent Analyses
                    </h2>

                    <span className="text-sm text-slate-500">
                      ATS Reports
                    </span>
                  </div>

                  <div className="space-y-4">
                    {data.recent_analyses.map((analysis) => (
                      <div
                        key={analysis.id}
                        onClick={() => navigate(`/analysis/${analysis.id}`)}
                        role="button"
                        tabIndex={0}
                        onKeyDown={(e) => {
                          if (e.key === "Enter" || e.key === " ") {
                            navigate(`/analysis/${analysis.id}`);
                          }
                        }}
                        className="
                          flex
                          items-center
                          justify-between
                          rounded-2xl
                          border
                          border-slate-200
                          p-4
                          hover:bg-slate-50
                          transition-all
                          cursor-pointer
                        "
                      >
                        <div>
                          <div className="font-medium text-slate-900">
                            Resume Analysis
                          </div>

                          <div className="text-sm text-slate-500">
                            {new Date(
                              analysis.created_at
                            ).toLocaleDateString()}
                          </div>
                        </div>

                        <div className="flex items-center gap-3">
                          <div
                            className="
                              rounded-full
                              bg-green-100
                              px-3
                              py-1
                              text-green-700
                              text-sm
                              font-semibold
                            "
                          >
                            {Math.round(
                              analysis.overall_score
                            )}
                            %
                          </div>

                          <ArrowUpRight size={18} />
                        </div>
                      </div>
                    ))}
                  </div>
                </Card>

                {/* Insights */}
                <Card className="p-8">
                  <h2 className="text-xl font-semibold mb-6">
                    Insights
                  </h2>

                  <div className="space-y-4">
                    <div className="rounded-2xl bg-blue-50 p-4 border border-blue-100">
                      <div className="font-medium text-blue-900">
                        ATS Optimization
                      </div>

                      <p className="text-sm text-blue-700 mt-2">
                        Improve keyword coverage to increase
                        interview opportunities.
                      </p>
                    </div>

                    <div className="rounded-2xl bg-violet-50 p-4 border border-violet-100">
                      <div className="font-medium text-violet-900">
                        Recruiter Readiness
                      </div>

                      <p className="text-sm text-violet-700 mt-2">
                        Continue improving resume alignment
                        with target roles.
                      </p>
                    </div>

                    <div className="rounded-2xl bg-green-50 p-4 border border-green-100">
                      <div className="font-medium text-green-900">
                        Skill Growth
                      </div>

                      <p className="text-sm text-green-700 mt-2">
                        Focus on missing skills highlighted
                        in your latest reports.
                      </p>
                    </div>
                  </div>
                </Card>
              </div>
            )}
          </>
        )}
      </div>
    </div>
  );
}

function StatCard({
  icon,
  label,
  value,
}: {
  icon: ReactNode;
  label: string;
  value: number | string;
}) {
  return (
    <Card className="p-6">
      <div
        className="
          w-12
          h-12
          rounded-2xl
          bg-gradient-to-r
          from-blue-600
          to-violet-600
          text-white
          flex
          items-center
          justify-center
          mb-4
        "
      >
        {icon}
      </div>

      <div className="text-3xl font-bold text-slate-900">
        {value}
      </div>

      <div className="text-sm text-slate-500 mt-1">
        {label}
      </div>
    </Card>
  );
}
