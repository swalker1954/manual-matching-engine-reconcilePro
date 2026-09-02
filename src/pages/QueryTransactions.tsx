import { useMemo, useState } from "react";
import Masthead from "../components/Masthead";
import StatusBadge from "../components/StatusBadge";
import { transactions, selectedMatchDetail, type TxnStatus } from "../data/mock";

const FILTERS: { label: string; value: TxnStatus | "ALL"; count: number; colorClass: string }[] = [
  { label: "All", value: "ALL", count: 1482, colorClass: "" },
  { label: "Matched", value: "MATCHED", count: 1024, colorClass: "text-matched" },
  { label: "Pending", value: "PENDING", count: 342, colorClass: "text-pending" },
  { label: "Unmatched", value: "UNMATCHED", count: 98, colorClass: "text-inkSoft" },
  { label: "Exception", value: "EXCEPTION", count: 18, colorClass: "text-exception" },
];

export default function QueryTransactions() {
  const [filter, setFilter] = useState<TxnStatus | "ALL">("ALL");
  const [selectedId, setSelectedId] = useState(selectedMatchDetail.txnId);

  const rows = useMemo(
    () => (filter === "ALL" ? transactions : transactions.filter((t) => t.status === filter)),
    [filter],
  );

  const detail = selectedMatchDetail;

  return (
    <div className="min-h-screen flex flex-col bg-paper text-ink">
      <Masthead />

      <div className="flex-1 px-7 py-5 flex flex-col gap-3.5 overflow-hidden">
        <div className="flex items-end justify-between border-b-2 border-ink pb-3">
          <div>
            <div className="font-display font-black text-[32px] tracking-tight">Query Transactions</div>
            <div className="text-xs text-inkSoft mt-0.5">
              Search and manually match records across all connected sources
            </div>
          </div>
          <button className="flex items-center gap-2 px-4.5 py-2.5 bg-ink text-paperCard text-xs font-bold tracking-wider hover:bg-crimson transition-colors px-[18px]">
            <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round">
              <line x1="12" y1="5" x2="12" y2="19" />
              <line x1="5" y1="12" x2="19" y2="12" />
            </svg>
            NEW MATCH
          </button>
        </div>

        <div className="bg-paperCard border-2 border-ink px-3.5 py-3 flex items-center gap-2.5 flex-wrap">
          <div className="flex-1 min-w-[220px] flex items-center gap-2 bg-paper border border-rule px-3 py-2">
            <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="#8c8379" strokeWidth="1.75" strokeLinecap="round" strokeLinejoin="round">
              <circle cx="11" cy="11" r="7" />
              <line x1="21" y1="21" x2="16.65" y2="16.65" />
            </svg>
            <span className="text-xs text-inkFaint">Search by transaction ID, reference, counterparty&hellip;</span>
          </div>
          <div className="flex items-center gap-2 px-3 py-2 border border-ink text-xs">
            <span>Aug 24 &ndash; Aug 31, 2026</span>
          </div>
          <div className="flex items-center gap-2 px-3 py-2 border border-ink text-xs">
            <span>All Sources</span>
          </div>
          <div className="w-px h-5.5 bg-rule h-[22px]" />
          <div className="flex items-center gap-1.5">
            {FILTERS.map((f) => (
              <button
                key={f.value}
                onClick={() => setFilter(f.value)}
                className={`px-3 py-1.5 text-[11px] font-semibold transition-colors ${
                  filter === f.value
                    ? "bg-crimson text-paperCard"
                    : `bg-paperCard border border-rule ${f.colorClass || "text-inkSoft"}`
                }`}
              >
                {f.label} {f.count.toLocaleString()}
              </button>
            ))}
          </div>
          <div className="flex-1" />
          <button
            onClick={() => setFilter("ALL")}
            className="text-[11px] text-inkSoft font-semibold hover:text-crimson"
          >
            CLEAR FILTERS
          </button>
        </div>

        <div className="flex-1 flex gap-4 min-h-0">
          <div className="flex-[1.7] bg-paperCard border-2 border-ink flex flex-col min-h-0 overflow-hidden">
            <div className="grid grid-cols-[100px_74px_66px_1.3fr_100px_86px_90px_60px] gap-2 px-4 py-2.5 bg-ink text-paper/85 text-[10px] tracking-wider">
              <div>TXN ID</div>
              <div>DATE</div>
              <div>SRC</div>
              <div>COUNTERPARTY</div>
              <div className="text-right">AMOUNT</div>
              <div>CONFIDENCE</div>
              <div>STATUS</div>
              <div className="text-right">&nbsp;</div>
            </div>
            <div className="flex-1 overflow-y-auto">
              {rows.map((txn) => (
                <button
                  key={txn.id}
                  onClick={() => setSelectedId(txn.id)}
                  className={`w-full grid grid-cols-[100px_74px_66px_1.3fr_100px_86px_90px_60px] gap-2 items-center px-4 py-2.5 border-b border-rule last:border-b-0 text-left text-[11.5px] hover:bg-black/[0.03] ${
                    selectedId === txn.id ? "bg-crimson/5 shadow-[inset_0_0_0_2px_theme(colors.crimson)]" : ""
                  }`}
                >
                  <div className={selectedId === txn.id ? "font-bold" : ""}>{txn.id}</div>
                  <div className="text-inkSoft">{txn.date}</div>
                  <div>
                    <span className="text-[9.5px] px-1.5 py-0.5 bg-black/5 text-inkSoft font-semibold">
                      {txn.source}
                    </span>
                  </div>
                  <div>{txn.counterparty}</div>
                  <div className="text-right">{txn.amount}</div>
                  <div className="flex items-center gap-1.5">
                    {txn.confidence != null ? (
                      <>
                        <div className="w-9 h-[5px] bg-black/10 overflow-hidden">
                          <div
                            className={`h-full ${
                              txn.status === "MATCHED"
                                ? "bg-matched"
                                : txn.status === "EXCEPTION"
                                  ? "bg-exception"
                                  : "bg-pending"
                            }`}
                            style={{ width: `${txn.confidence}%` }}
                          />
                        </div>
                        <span className="text-inkSoft">{txn.confidence}%</span>
                      </>
                    ) : (
                      <span className="text-inkFaint">&mdash;</span>
                    )}
                  </div>
                  <div>
                    <StatusBadge status={txn.status} />
                  </div>
                  <div className="text-right text-inkFaint">
                    <svg
                      className="inline-block"
                      width="14"
                      height="14"
                      viewBox="0 0 24 24"
                      fill="none"
                      stroke="currentColor"
                      strokeWidth="1.75"
                      strokeLinecap="round"
                      strokeLinejoin="round"
                    >
                      <path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z" />
                      <circle cx="12" cy="12" r="3" />
                    </svg>
                  </div>
                </button>
              ))}
            </div>
            <div className="flex items-center justify-between px-4 py-2.5 border-t-2 border-ink">
              <div className="text-[11px] text-inkSoft">
                Showing 1&ndash;{rows.length} of 1,482
              </div>
              <div className="flex items-center gap-1.5 text-[11px]">
                <span className="w-[26px] h-[26px] flex items-center justify-center text-inkSoft cursor-pointer">&lsaquo;</span>
                <span className="w-[26px] h-[26px] flex items-center justify-center bg-crimson text-paperCard font-bold">1</span>
                <span className="w-[26px] h-[26px] flex items-center justify-center text-inkSoft cursor-pointer">2</span>
                <span className="w-[26px] h-[26px] flex items-center justify-center text-inkSoft cursor-pointer">3</span>
                <span className="text-inkFaint">&hellip;</span>
                <span className="w-[26px] h-[26px] flex items-center justify-center text-inkSoft cursor-pointer">165</span>
                <span className="w-[26px] h-[26px] flex items-center justify-center text-inkSoft cursor-pointer">&rsaquo;</span>
              </div>
            </div>
          </div>

          <div className="w-[380px] flex-none bg-paperCard border-2 border-ink p-4.5 flex flex-col gap-4 overflow-y-auto p-[18px]">
            <div className="flex items-center justify-between">
              <div className="font-display font-extrabold text-base">Match Detail</div>
              <div className="text-[10px] px-2 py-0.5 bg-ink text-paperCard font-semibold">{detail.txnId}</div>
            </div>

            <div className="bg-exception text-paperCard p-4 flex flex-col items-center gap-1">
              <div className="font-display font-black text-[34px]">{detail.confidence}%</div>
              <div className="text-[10px] tracking-wider">MATCH CONFIDENCE &middot; LOW</div>
            </div>

            <div className="flex flex-col gap-2">
              <div className="text-[10px] tracking-wider text-inkSoft font-semibold">
                SOURCE RECORD &middot; {detail.source.label.toUpperCase()}
              </div>
              <div className="bg-paper border border-ink p-2.5 flex flex-col gap-1.5 text-[11.5px]">
                <Row label="Date" value={detail.source.date} />
                <Row label="Amount" value={detail.source.amount} warn />
                <Row label="Reference" value={detail.source.reference} />
                <Row label="Counterparty" value={detail.source.counterparty} />
              </div>
            </div>

            <div className="flex flex-col gap-2">
              <div className="text-[10px] tracking-wider text-inkSoft font-semibold">
                CANDIDATE MATCH &middot; {detail.candidate.label.toUpperCase()}
              </div>
              <div className="bg-paper border border-ink p-2.5 flex flex-col gap-1.5 text-[11.5px]">
                <Row label="Date" value={detail.candidate.date} ok={detail.candidate.dateMatches} />
                <Row label="Amount" value={detail.candidate.amount} warn={!detail.candidate.amountMatches} />
                <Row label="Reference" value={detail.candidate.reference} warn={!detail.candidate.referenceMatches} />
                <Row label="Counterparty" value={detail.candidate.counterparty} ok={detail.candidate.counterpartyMatches} />
              </div>
            </div>

            <div className="flex-1" />

            <div className="flex gap-2">
              <button className="flex-1 text-center py-2.5 bg-matched text-paperCard text-[11.5px] font-bold tracking-wide hover:opacity-90">
                CONFIRM MATCH
              </button>
              <button className="px-3.5 py-2.5 border border-exception text-exception text-[11.5px] font-bold hover:bg-exception hover:text-paperCard transition-colors">
                REJECT
              </button>
              <button className="px-3 py-2.5 text-inkSoft text-[11.5px] font-semibold hover:text-ink">
                SKIP
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

function Row({
  label,
  value,
  ok,
  warn,
}: {
  label: string;
  value: string;
  ok?: boolean;
  warn?: boolean;
}) {
  return (
    <div className="flex justify-between">
      <span className="text-inkSoft">{label}</span>
      <span className={warn ? "text-pending font-semibold" : ""}>
        {value} {ok && <span className="text-matched">&#10003;</span>}
        {warn && <span>&#9650;</span>}
      </span>
    </div>
  );
}
