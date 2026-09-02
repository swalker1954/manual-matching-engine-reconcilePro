export type EngineRunStatus = "RUNNING" | "ERROR" | "COMPLETE" | "QUEUED";

export interface EngineRun {
  id: string;
  source: string;
  origin: string;
  status: EngineRunStatus;
  progress: number;
  detail: string;
}

export const engineRuns: EngineRun[] = [
  { id: "RUN-4471", source: "ACH", origin: "First Horizon", status: "RUNNING", progress: 62, detail: "842 rec/s · ETA 2m" },
  { id: "RUN-4470", source: "WIRE", origin: "JPM Chase", status: "RUNNING", progress: 88, detail: "1,120 rec/s · ETA 40s" },
  { id: "RUN-4469", source: "CHECK", origin: "Regions Bank", status: "ERROR", progress: 34, detail: "retry 2 of 3" },
  { id: "RUN-4468", source: "ACH", origin: "Wells Fargo", status: "COMPLETE", progress: 100, detail: "10,204 records" },
  { id: "RUN-4467", source: "WIRE", origin: "PNC Bank", status: "QUEUED", progress: 0, detail: "queued 4m ago" },
];

export interface ExceptionItem {
  id: string;
  title: string;
  runId: string;
  source: string;
  amount: string;
  age: string;
  severity: "high" | "medium";
}

export const exceptions: ExceptionItem[] = [
  { id: "e1", title: "Amount Mismatch", runId: "RUN-4469", source: "Wire", amount: "$12,450.00", age: "2m", severity: "high" },
  { id: "e2", title: "Missing Reference", runId: "RUN-4468", source: "Check", amount: "$3,050.00", age: "6m", severity: "medium" },
  { id: "e3", title: "Duplicate Candidate", runId: "RUN-4460", source: "ACH", amount: "$890.50", age: "14m", severity: "high" },
  { id: "e4", title: "Date Out of Window", runId: "RUN-4457", source: "Wire", amount: "$56,780.00", age: "22m", severity: "medium" },
  { id: "e5", title: "Counterparty Unknown", runId: "RUN-4450", source: "ACH", amount: "$1,340.25", age: "31m", severity: "high" },
];

export type TxnStatus = "MATCHED" | "PENDING" | "UNMATCHED" | "EXCEPTION";

export interface Transaction {
  id: string;
  date: string;
  source: string;
  counterparty: string;
  amount: string;
  confidence: number | null;
  status: TxnStatus;
}

export const transactions: Transaction[] = [
  { id: "TXN-88214", date: "08/31/26", source: "ACH", counterparty: "Meridian Supply Co.", amount: "$4,230.00", confidence: 98, status: "MATCHED" },
  { id: "TXN-88213", date: "08/31/26", source: "WIRE", counterparty: "Coastal Logistics", amount: "$12,450.00", confidence: 41, status: "EXCEPTION" },
  { id: "TXN-88212", date: "08/30/26", source: "ACH", counterparty: "Nova Retail Group", amount: "$890.50", confidence: 100, status: "MATCHED" },
  { id: "TXN-88211", date: "08/30/26", source: "CHECK", counterparty: "Bramwell Estates", amount: "$2,100.00", confidence: null, status: "PENDING" },
  { id: "TXN-88210", date: "08/30/26", source: "WIRE", counterparty: "Falcon Industrial", amount: "$56,780.00", confidence: 76, status: "PENDING" },
  { id: "TXN-88209", date: "08/29/26", source: "ACH", counterparty: "Meridian Supply Co.", amount: "$4,230.00", confidence: null, status: "UNMATCHED" },
  { id: "TXN-88208", date: "08/29/26", source: "WIRE", counterparty: "Coastal Logistics", amount: "$9,120.00", confidence: 100, status: "MATCHED" },
  { id: "TXN-88207", date: "08/29/26", source: "ACH", counterparty: "Verdant Foods", amount: "$1,340.25", confidence: 89, status: "MATCHED" },
  { id: "TXN-88206", date: "08/28/26", source: "CHECK", counterparty: "Bramwell Estates", amount: "$3,050.00", confidence: 22, status: "EXCEPTION" },
];

export const selectedMatchDetail = {
  txnId: "TXN-88213",
  confidence: 41,
  source: {
    label: "Wire Transfer System",
    date: "08/31/2026",
    amount: "$12,450.00",
    reference: "REF-WT-88213X",
    counterparty: "Coastal Logistics",
  },
  candidate: {
    label: "General Ledger",
    date: "08/31/2026",
    dateMatches: true,
    amount: "$12,405.00",
    amountMatches: false,
    reference: "REF-GL-4412A",
    referenceMatches: false,
    counterparty: "Coastal Logistics",
    counterpartyMatches: true,
  },
};
