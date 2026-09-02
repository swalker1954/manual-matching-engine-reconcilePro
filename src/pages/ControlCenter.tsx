import Masthead from "../components/Masthead";
import StatTile from "../components/StatTile";
import ProgressBar from "../components/ProgressBar";
import { engineRuns, exceptions, type EngineRunStatus } from "../data/mock";

const STATUS_COLOR: Record<EngineRunStatus, { text: string; bar: string }> = {
  RUNNING: { text: "text-crimson", bar: "bg-crimson" },
  ERROR: { text: "text-exception", bar: "bg-exception" },
  COMPLETE: { text: "text-matched", bar: "bg-matched" },
  QUEUED: { text: "text-inkFaint", bar: "bg-inkFaint" },
};

export default function ControlCenter() {
  return (
    <div className="min-h-screen flex flex-col bg-paper text-ink">
      <Masthead />

      <div className="flex-1 px-7 py-6 flex flex-col gap-4 overflow-hidden">
        <div className="flex items-end justify-between border-b-2 border-ink pb-3">
          <div>
            <div className="font-display font-black text-[32px] tracking-tight">Control Center</div>
            <div className="text-xs text-inkSoft mt-0.5">
              Real-time visibility into matching operations across all connected sources
            </div>
          </div>
          <button className="w-[34px] h-[34px] border-2 border-ink flex items-center justify-center text-ink hover:bg-ink hover:text-paperCard transition-colors">
            <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
              <polyline points="23 4 23 10 17 10" />
              <polyline points="1 20 1 14 7 14" />
              <path d="M20.49 9A9 9 0 0 0 5.64 5.64L1 10m22 4l-4.64 4.36A9 9 0 0 1 3.51 15" />
            </svg>
          </button>
        </div>

        <div className="grid grid-cols-[1.4fr_1fr_1fr_1fr_1fr] gap-3.5">
          <StatTile variant="hero" label="MATCH RATE" value="98.4%" trend="+0.6% vs yesterday" />
          <StatTile label="AUTO-MATCHED TODAY" value="12,847" trend="+1,204 since 9AM" />
          <StatTile label="PENDING REVIEW" value="342" trend="+18 last hour" />
          <StatTile variant="dark" label="OPEN EXCEPTIONS" value="18" trend="+4 need attention" />
          <StatTile label="VOLUME PROCESSED" value="$84.2M" trend="+2.1% last 24h" />
        </div>

        <div className="flex-1 flex gap-4.5 min-h-0 gap-[18px]">
          <div className="flex-[1.6] flex flex-col min-h-0">
            <div className="flex items-baseline justify-between border-t-2 border-ink pt-2 mb-1.5">
              <div className="font-display font-extrabold text-[15px]">
                <span className="text-crimson">01</span> &mdash; Engine Runs
              </div>
              <button className="text-[10.5px] tracking-wider text-crimson font-semibold hover:opacity-70">
                VIEW ALL &rarr;
              </button>
            </div>
            <div className="flex-1 bg-paperCard border-2 border-ink overflow-hidden flex flex-col">
              {engineRuns.map((run) => {
                const colors = STATUS_COLOR[run.status];
                return (
                  <div
                    key={run.id}
                    className="flex items-center justify-between px-4 py-2.5 border-b border-rule last:border-b-0 hover:bg-black/[0.03] cursor-pointer"
                  >
                    <div className="flex items-center gap-2.5 w-[230px]">
                      <span className={`w-[7px] h-[7px] ${colors.bar}`} />
                      <div>
                        <div className="text-xs font-semibold">{run.id}</div>
                        <div className="text-[10px] text-inkFaint">
                          {run.source} &middot; {run.origin}
                        </div>
                      </div>
                    </div>
                    <div className={`text-[10px] font-semibold w-[74px] ${colors.text}`}>{run.status}</div>
                    <ProgressBar percent={run.progress} colorClass={colors.bar} />
                    <div className="text-[10px] text-inkSoft text-right w-[130px]">{run.detail}</div>
                  </div>
                );
              })}
            </div>
          </div>

          <div className="flex-1 flex flex-col min-h-0">
            <div className="flex items-baseline justify-between border-t-2 border-ink pt-2 mb-1.5">
              <div className="font-display font-extrabold text-[15px]">
                <span className="text-crimson">02</span> &mdash; Exceptions Desk
              </div>
              <div className="text-[10px] px-2 py-0.5 bg-ink text-paperCard font-semibold">18 OPEN</div>
            </div>
            <div className="flex-1 bg-paperCard border-2 border-ink overflow-y-auto flex flex-col">
              {exceptions.map((ex) => (
                <div
                  key={ex.id}
                  className="flex items-start gap-2.5 px-3.5 py-2.5 border-b border-rule last:border-b-0 hover:bg-black/[0.03] cursor-pointer"
                >
                  <span
                    className={`w-[7px] h-[7px] mt-1 flex-none ${
                      ex.severity === "high" ? "bg-exception" : "bg-gold"
                    }`}
                  />
                  <div className="flex-1">
                    <div className="font-display font-bold text-[12.5px]">{ex.title}</div>
                    <div className="text-[10px] text-inkFaint mt-0.5">
                      {ex.runId} &middot; {ex.source} &middot; {ex.amount}
                    </div>
                  </div>
                  <div className="text-[10px] text-inkSoft">{ex.age}</div>
                </div>
              ))}
            </div>
          </div>
        </div>

        <div className="h-[52px] flex-none bg-ink border-t-[3px] border-crimson flex items-center justify-between px-5 text-[10.5px] text-paperCard/75">
          <div>API LATENCY <span className="text-paperCard font-semibold">42ms</span></div>
          <div className="w-px h-4 bg-paperCard/20" />
          <div>QUEUE DEPTH <span className="text-paperCard font-semibold">1,204</span></div>
          <div className="w-px h-4 bg-paperCard/20" />
          <div>UPTIME <span className="text-paperCard font-semibold">99.98%</span></div>
          <div className="w-px h-4 bg-paperCard/20" />
          <div>THROUGHPUT <span className="text-paperCard font-semibold">340 rec/s</span></div>
          <div className="w-px h-4 bg-paperCard/20" />
          <div>DATA SOURCES <span className="text-paperCard font-semibold">6/6 CONNECTED</span></div>
        </div>
      </div>
    </div>
  );
}
