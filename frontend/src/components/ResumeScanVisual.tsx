import { motion } from "framer-motion";

// The product's signature visual: a stylized resume document with a
// scan line sweeping down it, highlighting skill terms as it passes —
// a literal depiction of "this is what the algorithm sees", which is
// the actual emotional core of the product (demystifying the ATS
// black box), rather than a generic dashboard mockup.

const LINES = [
  { width: "72%", highlight: false },
  { width: "45%", highlight: false },
  { width: "0%", highlight: false, gap: true },
  { width: "38%", highlight: false, bold: true },
  { width: "85%", highlight: false },
  { width: "63%", highlight: true, label: "Python" },
  { width: "70%", highlight: false },
  { width: "55%", highlight: true, label: "FastAPI" },
  { width: "0%", highlight: false, gap: true },
  { width: "30%", highlight: false, bold: true },
  { width: "90%", highlight: false },
  { width: "58%", highlight: true, label: "PostgreSQL" },
  { width: "75%", highlight: false },
  { width: "40%", highlight: true, label: "Docker" },
  { width: "67%", highlight: false },
];

export function ResumeScanVisual() {
  return (
    <div className="relative w-full max-w-sm mx-auto select-none" aria-hidden="true">
      <div className="relative rounded-lg border border-line bg-white shadow-card overflow-hidden">
        {/* Document content */}
        <div className="p-6 space-y-2.5">
          {LINES.map((line, i) =>
            line.gap ? (
              <div key={i} className="h-2" />
            ) : (
              <div key={i} className="relative flex items-center gap-2">
                <div
                  className={
                    line.bold
                      ? "h-2.5 rounded-sm bg-ink/70"
                      : line.highlight
                      ? "h-2 rounded-sm bg-match/25 ring-1 ring-match/40"
                      : "h-2 rounded-sm bg-ink/10"
                  }
                  style={{ width: line.width }}
                />
                {line.highlight && line.label && (
                  <span className="font-mono text-[10px] text-match font-medium whitespace-nowrap">
                    {line.label}
                  </span>
                )}
              </div>
            )
          )}
        </div>

        {/* Scan line sweep */}
        <motion.div
          className="absolute inset-x-0 h-full pointer-events-none"
          initial={{ y: "-100%" }}
          animate={{ y: "100%" }}
          transition={{ duration: 2.8, repeat: Infinity, ease: "easeInOut", repeatType: "loop" }}
        >
          <div className="h-px w-full bg-accent shadow-[0_0_12px_2px_rgba(37,99,235,0.5)]" />
          <div className="h-16 w-full bg-gradient-to-b from-accent/[0.07] to-transparent" />
        </motion.div>
      </div>

      {/* Floating score badge */}
      <motion.div
        initial={{ opacity: 0, scale: 0.9, y: 8 }}
        animate={{ opacity: 1, scale: 1, y: 0 }}
        transition={{ delay: 0.4, duration: 0.5 }}
        className="absolute -right-4 -bottom-4 bg-ink text-paper rounded-lg shadow-card-hover px-4 py-3"
      >
        <div className="font-mono text-2xl font-semibold leading-none">87</div>
        <div className="text-[10px] text-paper/60 mt-1 tracking-wide uppercase">ATS Score</div>
      </motion.div>
    </div>
  );
}
