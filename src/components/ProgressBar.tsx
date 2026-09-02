export default function ProgressBar({
  percent,
  colorClass,
  widthClass = "w-[130px]",
}: {
  percent: number;
  colorClass: string;
  widthClass?: string;
}) {
  return (
    <div className={`${widthClass} h-[5px] bg-black/10 overflow-hidden`}>
      <div className={`h-full ${colorClass}`} style={{ width: `${percent}%` }} />
    </div>
  );
}
