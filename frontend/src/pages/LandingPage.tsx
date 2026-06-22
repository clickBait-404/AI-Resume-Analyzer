import { Link } from "react-router-dom";
import { motion } from "framer-motion";
import { Navbar } from "../components/Navbar";
import { Button } from "../components/Button";
import { Card } from "../components/Card";
import { ResumeScanVisual } from "../components/ResumeScanVisual";

const FEATURES = [
  {
    title: "ATS compatibility score",
    description:
      "A 0–100 score broken into five components — skill match, keyword coverage, experience, education, completeness — each one explained, never a black box.",
  },
  {
    title: "Skill gap analysis",
    description:
      "See exactly which required and preferred skills are missing from your resume, ranked by priority, with a stated reason for each.",
  },
  {
    title: "Recruiter simulation",
    description:
      "Get a first-pass screening verdict — would this resume get shortlisted, what stands out, what raises concerns.",
  },
  {
    title: "Interview preparation",
    description:
      "A tailored set of technical, behavioral, project-based, and resume-based questions, with answer rubrics and follow-ups.",
  },
  {
    title: "Resume rewriting",
    description:
      "Turn vague bullets into specific, high-impact statements — without fabricated metrics standing in for real ones.",
  },
  {
    title: "30/60/90-day roadmap",
    description:
      "A concrete, week-by-week plan to close your specific skill gaps before your next application cycle.",
  },
];

export function LandingPage() {
  return (
    <div className="min-h-screen flex flex-col">
      <Navbar />

      {/* Hero */}
      <section className="container-page pt-16 pb-24 md:pt-24 md:pb-32">
        <div className="grid md:grid-cols-2 gap-16 items-center">
          <motion.div
            initial={{ opacity: 0, y: 16 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.7, ease: [0.16, 1, 0.3, 1] }}
          >
            <h1 className="font-display text-hero font-medium text-ink">
              Know how recruiters see your resume.
            </h1>
            <p className="mt-6 text-lg text-slate leading-relaxed max-w-md">
              Analyze your resume against real job descriptions and receive ATS
              insights, recruiter feedback, and interview preparation guidance —
              every score explained, nothing left a mystery.
            </p>
            <div className="mt-8 flex flex-wrap items-center gap-4">
              <Link to="/register">
                <Button variant="primary" size="lg">
                  Analyze your resume
                </Button>
              </Link>
              <a href="#how-it-works">
                <Button variant="secondary" size="lg">
                  See how it works
                </Button>
              </a>
            </div>
          </motion.div>

          <motion.div
            initial={{ opacity: 0, scale: 0.96 }}
            animate={{ opacity: 1, scale: 1 }}
            transition={{ duration: 0.8, delay: 0.15, ease: [0.16, 1, 0.3, 1] }}
          >
            <ResumeScanVisual />
          </motion.div>
        </div>
      </section>

      {/* Features */}
      <section id="how-it-works" className="border-t border-line bg-white">
        <div className="container-page py-20">
          <div className="max-w-xl mb-12">
            <h2 className="font-display text-3xl font-medium text-ink">
              Every layer of the job search, covered.
            </h2>
            <p className="mt-3 text-slate">
              Rule-based scoring you can audit, plus AI feedback that reads like an
              experienced recruiter — not a chatbot.
            </p>
          </div>

          <div className="grid sm:grid-cols-2 lg:grid-cols-3 gap-5">
            {FEATURES.map((feature) => (
              <Card key={feature.title} className="p-6">
                <h3 className="font-semibold text-ink">{feature.title}</h3>
                <p className="mt-2 text-sm text-slate leading-relaxed">{feature.description}</p>
              </Card>
            ))}
          </div>
        </div>
      </section>

      {/* CTA */}
      <section className="border-t border-line">
        <div className="container-page py-20 text-center">
          <h2 className="font-display text-3xl font-medium text-ink">
            Stop guessing why you're not hearing back.
          </h2>
          <p className="mt-3 text-slate max-w-md mx-auto">
            Upload your resume, paste a job description, and see exactly where it
            stands in under a minute.
          </p>
          <div className="mt-8">
            <Link to="/register">
              <Button variant="primary" size="lg">
                Get started — it's free
              </Button>
            </Link>
          </div>
        </div>
      </section>

      <footer className="border-t border-line">
        <div className="container-page py-8 text-sm text-slate-light flex items-center justify-between">
          <span>Resumeter</span>
          <span>Rule-based ATS scoring. No black boxes.</span>
        </div>
      </footer>
    </div>
  );
}
