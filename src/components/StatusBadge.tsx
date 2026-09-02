import type { TxnStatus } from "../data/mock";

const STYLES: Record<TxnStatus, string> = {
  MATCHED: "bg-matchedDim text-matched border border-matched/40",
  PENDING: "bg-pendingDim text-pending border border-pending/40",
  UNMATCHED: "bg-black/5 text-inkSoft border border-inkFaint/40",
  EXCEPTION: "bg-crimson text-paperCard border border-crimson",
};

export default function StatusBadge({ status }: { status: TxnStatus }) {
  return (
    <span className={`text-[9.5px] px-1.5 py-1 font-bold tracking-wide ${STYLES[status]}`}>
      {status}
    </span>
  );
}
