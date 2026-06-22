import { useState, type ChangeEvent, type FormEvent } from "react";
import { useNavigate } from "react-router-dom";
import { Navbar } from "../components/Navbar";
import { Card } from "../components/Card";
import { Button } from "../components/Button";
import { api, extractErrorMessage } from "../lib/api";

export function AnalyzePage() {
  const navigate = useNavigate();

  const [file, setFile] = useState<File | null>(null);
  const [jdText, setJdText] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [stage, setStage] = useState<string>("");

  const handleFileChange = (e: ChangeEvent<HTMLInputElement>) => {
    const selected = e.target.files?.[0];
    if (selected) setFile(selected);
  };

  const handleSubmit = async (e: FormEvent) => {
    e.preventDefault();
    setError(null);

    if (!file) {
      setError("Please select a resume file (PDF or DOCX).");
      return;
    }
    if (jdText.trim().length < 20) {
      setError("Please paste a job description (at least 20 characters).");
      return;
    }

    setIsSubmitting(true);
    try {
      setStage("Uploading and parsing your resume…");
      const resume = await api.resume.upload(file);

      setStage("Analyzing the job description…");
      const jd = await api.jobDescription.create(jdText);

      setStage("Scoring your resume against this role…");
      const result = await api.analysis.run(resume.id, jd.id, true);

      navigate(`/analysis/${result.id}`);
    } catch (err) {
      setError(extractErrorMessage(err));
      setStage("");
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <div className="min-h-screen flex flex-col">
      <Navbar />
      <div className="container-page py-12 flex-1 max-w-3xl">
        <h1 className="font-display text-3xl font-medium text-ink">New analysis</h1>
        <p className="mt-2 text-slate">
          Upload your resume and paste the job description you're targeting.
        </p>

        <Card className="p-8 mt-8">
          <form onSubmit={handleSubmit} className="flex flex-col gap-6" noValidate>
            <div>
              <label htmlFor="resume-file" className="text-sm font-medium text-ink block mb-2">
                Resume (PDF or DOCX)
              </label>
              <input
                id="resume-file"
                type="file"
                accept=".pdf,.docx"
                onChange={handleFileChange}
                className="block w-full text-sm text-slate file:mr-4 file:py-2 file:px-4 file:rounded file:border file:border-line file:bg-paper file:text-sm file:font-medium file:text-ink hover:file:bg-ink/[0.03] file:cursor-pointer cursor-pointer"
              />
              {file && <p className="mt-2 text-sm text-match">Selected: {file.name}</p>}
            </div>

            <div>
              <label htmlFor="jd-text" className="text-sm font-medium text-ink block mb-2">
                Job description
              </label>
              <textarea
                id="jd-text"
                rows={10}
                value={jdText}
                onChange={(e) => setJdText(e.target.value)}
                placeholder="Paste the full job description here…"
                className="w-full px-3.5 py-2.5 rounded border border-line bg-white text-sm text-ink placeholder:text-slate-light focus:outline-none focus-visible:ring-2 focus-visible:ring-accent focus-visible:border-accent resize-y"
              />
            </div>

            {error && (
              <div role="alert" className="text-sm text-gap bg-gap-dim border border-gap/20 rounded px-3 py-2">
                {error}
              </div>
            )}

            {isSubmitting && stage && (
              <div className="text-sm text-slate flex items-center gap-2">
                <span className="inline-block h-1.5 w-1.5 rounded-full bg-accent animate-pulse" />
                {stage}
              </div>
            )}

            <Button type="submit" variant="primary" size="lg" disabled={isSubmitting}>
              {isSubmitting ? "Analyzing…" : "Run analysis"}
            </Button>
          </form>
        </Card>
      </div>
    </div>
  );
}
