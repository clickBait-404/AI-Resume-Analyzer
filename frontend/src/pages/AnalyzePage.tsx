import { useState, type ChangeEvent, type FormEvent } from "react";
import { useNavigate } from "react-router-dom";
import { Upload, FileText, Sparkles } from "lucide-react";

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
  const [stage, setStage] = useState("");

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
      setError(
        "Please paste a job description (at least 20 characters)."
      );
      return;
    }

    setIsSubmitting(true);

    try {
      setStage("Uploading and parsing your resume...");
      const resume = await api.resume.upload(file);

      setStage("Analyzing the job description...");
      const jd = await api.jobDescription.create(jdText);

      setStage("Scoring your resume against this role...");
      const result = await api.analysis.run(
        resume.id,
        jd.id,
        true
      );

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

      <div className="container-page py-12 flex-1 max-w-4xl">
        {/* Header */}
        <div className="mb-10">
          <div className="badge-pill mb-4">
            <Sparkles size={16} />
            ATS Resume Intelligence
          </div>

          <h1 className="text-5xl font-bold tracking-tight text-slate-900">
            Analyze Your Resume
          </h1>

          <p className="mt-4 text-lg text-slate-600 max-w-2xl">
            Upload your resume, paste a job description,
            and receive ATS scoring, recruiter feedback,
            skill-gap analysis and optimization
            suggestions.
          </p>
        </div>

        {/* Main Card */}
        <Card className="p-10">
          <form
            onSubmit={handleSubmit}
            className="flex flex-col gap-8"
            noValidate
          >
            {/* Upload Section */}
            <div>
              <label
                htmlFor="resume-file"
                className="
                  block
                  text-sm
                  font-semibold
                  text-slate-900
                  mb-3
                "
              >
                Resume Upload
              </label>

              <div
                className="
                  border-2
                  border-dashed
                  border-slate-300
                  rounded-3xl
                  p-10
                  text-center
                  bg-slate-50/50
                  hover:border-blue-500
                  transition-all
                "
              >
                <Upload
                  size={36}
                  className="mx-auto text-blue-600 mb-4"
                />

                <h3 className="font-semibold text-slate-900">
                  Upload Your Resume
                </h3>

                <p className="text-sm text-slate-500 mt-2">
                  PDF and DOCX files supported
                </p>

                <input
                  id="resume-file"
                  type="file"
                  accept=".pdf,.docx"
                  onChange={handleFileChange}
                  className="mt-6 block mx-auto"
                />
              </div>

              {file && (
                <div
                  className="
                    mt-4
                    rounded-2xl
                    border
                    border-green-200
                    bg-green-50
                    p-4
                    flex
                    items-center
                    gap-3
                  "
                >
                  <FileText
                    size={18}
                    className="text-green-600"
                  />

                  <span className="text-sm text-green-700">
                    {file.name}
                  </span>
                </div>
              )}
            </div>

            {/* Job Description */}
            <div>
              <label
                htmlFor="jd-text"
                className="
                  block
                  text-sm
                  font-semibold
                  text-slate-900
                  mb-3
                "
              >
                Job Description
              </label>

              <textarea
                id="jd-text"
                rows={12}
                value={jdText}
                onChange={(e) => setJdText(e.target.value)}
                placeholder="Paste the full job description here..."
                className="
                  w-full
                  rounded-3xl
                  border
                  border-slate-200
                  bg-white
                  px-5
                  py-4
                  text-sm
                  text-slate-900
                  placeholder:text-slate-400
                  focus:border-blue-500
                  focus:ring-4
                  focus:ring-blue-100
                  outline-none
                  transition-all
                  resize-y
                "
              />
            </div>

            {/* Error */}
            {error && (
              <div
                role="alert"
                className="
                  rounded-2xl
                  bg-red-50
                  border
                  border-red-200
                  text-red-700
                  px-4
                  py-3
                  text-sm
                "
              >
                {error}
              </div>
            )}

            {/* Loading */}
            {isSubmitting && stage && (
              <div
                className="
                  rounded-2xl
                  bg-blue-50
                  border
                  border-blue-100
                  p-4
                  text-blue-700
                  flex
                  items-center
                  gap-3
                "
              >
                <span
                  className="
                    h-2
                    w-2
                    rounded-full
                    bg-blue-600
                    animate-pulse
                  "
                />

                {stage}
              </div>
            )}

            {/* Submit */}
            <Button
              type="submit"
              variant="primary"
              size="lg"
              disabled={isSubmitting}
              className="w-full"
            >
              {isSubmitting
                ? "Analyzing Resume..."
                : "Run ATS Analysis"}
            </Button>
          </form>
        </Card>
      </div>
    </div>
  );
}
