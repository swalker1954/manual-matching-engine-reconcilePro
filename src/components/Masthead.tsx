import { NavLink } from "react-router-dom";

const NAV_ITEMS = [
  { label: "Control Center", to: "/control-center" },
  { label: "Query", to: "/query" },
  { label: "Exceptions", to: "/exceptions", badge: true },
  { label: "Rules", to: "/rules" },
  { label: "Audit", to: "/audit" },
];

export default function Masthead() {
  return (
    <div className="flex-none">
      <div className="h-[76px] flex items-center justify-between px-7 border-b-[3px] border-ink">
        <div className="flex items-center gap-3.5">
          <div className="w-[38px] h-[38px] bg-crimson flex items-center justify-center">
            <div className="w-4 h-4 border-2 border-paperCard" />
          </div>
          <div>
            <div className="font-display font-black text-2xl leading-none tracking-tight">
              Reconcile<span className="text-crimson italic">Pro</span>
            </div>
            <div className="text-[9.5px] tracking-[0.18em] text-inkSoft mt-1">
              MANUAL MATCHING ENGINE &middot; LIVE EDITION
            </div>
          </div>
        </div>

        <div className="flex items-center gap-4">
          <div className="flex items-center gap-1.5 px-3 py-1.5 bg-crimson text-paperCard">
            <span className="w-1.5 h-1.5 rounded-full bg-paperCard" />
            <span className="text-[11px] tracking-wider font-semibold">LIVE &middot; PRODUCTION</span>
          </div>
          <div className="text-[11px] text-inkSoft text-right leading-relaxed">
            <div>MON, AUG 31 2026</div>
            <div className="font-semibold">6 / 6 SOURCES CONNECTED</div>
          </div>
          <div className="w-8 h-8 rounded-full bg-ink text-paperCard flex items-center justify-center font-display font-bold text-xs border-2 border-gold">
            SW
          </div>
        </div>
      </div>

      <div className="h-11 flex items-center gap-6 px-7 border-b border-rule bg-paperCard">
        {NAV_ITEMS.map((item) => (
          <NavLink
            key={item.to}
            to={item.to}
            className={({ isActive }) =>
              `relative text-[11.5px] tracking-wider transition-colors ${
                isActive
                  ? "font-bold text-crimson border-b-[3px] border-crimson pb-3.5 -mb-[15px]"
                  : "text-inkSoft hover:text-crimson"
              }`
            }
          >
            {({ isActive }) => (
              <>
                {item.label.toUpperCase()}
                {item.badge && !isActive && (
                  <span className="absolute -top-0.5 -right-3.5 w-1.5 h-1.5 rounded-full bg-crimson" />
                )}
              </>
            )}
          </NavLink>
        ))}
        <div className="flex-1" />
        <NavLink
          to="/settings"
          className={({ isActive }) =>
            `text-[11.5px] tracking-wider ${isActive ? "font-bold text-crimson" : "text-inkSoft hover:text-crimson"}`
          }
        >
          SETTINGS
        </NavLink>
      </div>
    </div>
  );
}
