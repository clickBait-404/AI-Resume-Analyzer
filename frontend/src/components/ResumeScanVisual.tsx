import { motion } from "framer-motion";

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
    <div
      className="
      relative
      w-full
      max-w-lg
      mx-auto
      select-none
      "
      aria-hidden="true"
    >
      {/* Floating ATS Card */}
      <motion.div
        animate={{ y: [0, -6, 0] }}
        transition={{
          duration: 4,
          repeat: Infinity,
          ease: "easeInOut",
        }}
        className="
        absolute
        -left-12
        top-12
        z-20
        glass-card
        rounded-2xl
        px-4
        py-3
        "
      >
        <div className="text-xs text-slate-500">
          Keyword Match
        </div>

        <div className="text-2xl font-bold text-green-600">
          92%
        </div>
      </motion.div>

      {/* Floating Skills Card */}
      <motion.div
        animate={{ y: [0, 8, 0] }}
        transition={{
          duration: 5,
          repeat: Infinity,
          ease: "easeInOut",
        }}
        className="
        absolute
        -right-10
        top-24
        z-20
        glass-card
        rounded-2xl
        px-4
        py-3
        "
      >
        <div className="text-xs text-slate-500">
          Skills Match
        </div>

        <div className="text-2xl font-bold text-blue-600">
          88%
        </div>
      </motion.div>

      {/* Floating Experience Card */}
      <motion.div
        animate={{ y: [0, -8, 0] }}
        transition={{
          duration: 6,
          repeat: Infinity,
          ease: "easeInOut",
        }}
        className="
        absolute
        -left-8
        bottom-16
        z-20
        glass-card
        rounded-2xl
        px-4
        py-3
        "
      >
        <div className="text-xs text-slate-500">
          Experience
        </div>

        <div className="text-2xl font-bold text-violet-600">
          84%
        </div>
      </motion.div>

      {/* Main Resume Card */}
      <div
        className="
        relative
        overflow-hidden
        rounded-3xl
        bg-white/80
        backdrop-blur-xl
        border
        border-white/60
        shadow-[0_20px_60px_rgba(15,23,42,.12)]
        "
      >
        <div className="p-8 space-y-3">
          {LINES.map((line, i) =>
            line.gap ? (
              <div key={i} className="h-3" />
            ) : (
              <div
                key={i}
                className="relative flex items-center gap-2"
              >
                <div
                  className={
                    line.bold
                      ? "h-3 rounded bg-slate-700"
                      : line.highlight
                      ? "h-2.5 rounded bg-green-200 ring-1 ring-green-400"
                      : "h-2.5 rounded bg-slate-200"
                  }
                  style={{ width: line.width }}
                />

                {line.highlight && line.label && (
                  <span
                    className="
                    text-[11px]
                    font-semibold
                    text-green-600
                    whitespace-nowrap
                    "
                  >
                    {line.label}
                  </span>
                )}
              </div>
            )
          )}
        </div>

        {/* ATS Scanner */}
        <motion.div
          className="absolute inset-x-0 h-full pointer-events-none"
          initial={{ y: "-100%" }}
          animate={{ y: "100%" }}
          transition={{
            duration: 3,
            repeat: Infinity,
            ease: "easeInOut",
          }}
        >
          <div className="h-[2px] w-full bg-blue-500 shadow-[0_0_18px_3px_rgba(59,130,246,.7)]" />

          <div className="h-20 w-full bg-gradient-to-b from-blue-500/10 to-transparent" />
        </motion.div>
      </div>

      {/* ATS Score */}
      <motion.div
        initial={{
          opacity: 0,
          scale: 0.9,
          y: 8,
        }}
        animate={{
          opacity: 1,
          scale: 1,
          y: 0,
        }}
        transition={{
          delay: 0.4,
          duration: 0.5,
        }}
        className="
        absolute
        -right-6
        -bottom-6
        z-30
        rounded-3xl
        bg-gradient-to-r
        from-blue-600
        to-violet-600
        px-6
        py-5
        text-white
        shadow-2xl
        "
      >
        <div className="text-4xl font-bold leading-none">
          87
        </div>

        <div className="text-xs uppercase tracking-wider text-white/80 mt-2">
          ATS Score
        </div>
      </motion.div>
    </div>
  );
}
