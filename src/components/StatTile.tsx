type Variant = "hero" | "default" | "dark";

export default function StatTile({
  label,
  value,
  trend,
  variant = "default",
}: {
  label: string;
  value: string;
  trend: string;
  variant?: Variant;
}) {
  if (variant === "hero") {
    return (
      <div className="bg-crimson text-paperCard p-4.5 flex flex-col gap-2 justify-between p-[18px]">
        <div className="text-[10.5px] tracking-wider opacity-85">{label}</div>
        <div className="font-display font-black text-[46px] leading-none">{value}</div>
        <div className="flex items-center gap-1.5 text-[11px]">
          <span>&#9650;</span>
          <span>{trend}</span>
        </div>
      </div>
    );
  }

  if (variant === "dark") {
    return (
      <div className="bg-ink text-paperCard p-4 flex flex-col gap-2 justify-between">
        <div className="text-[10px] tracking-wider text-gold/80">{label}</div>
        <div className="font-display font-extrabold text-[26px] text-crimson/90">{value}</div>
        <div className="flex items-center gap-1.5 text-[10.5px] text-crimson/80">
          <span>&#9650;</span>
          <span>{trend}</span>
        </div>
      </div>
    );
  }

  return (
    <div className="bg-paperCard border-2 border-ink p-4 flex flex-col gap-2 justify-between">
      <div className="text-[10px] tracking-wider text-inkSoft">{label}</div>
      <div className="font-display font-extrabold text-[26px]">{value}</div>
      <div className="flex items-center gap-1.5 text-[10.5px] text-matched">
        <span>&#9650;</span>
        <span>{trend}</span>
      </div>
    </div>
  );
}
