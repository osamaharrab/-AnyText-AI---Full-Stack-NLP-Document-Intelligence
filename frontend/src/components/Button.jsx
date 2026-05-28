export function Button({
  children,
  icon: Icon,
  variant = 'secondary',
  className = '',
  type = 'button',
  ...props
}) {
  const variants = {
    primary: 'bg-brand-600 text-white border-brand-600 hover:bg-brand-700',
    secondary: 'bg-white text-slate-800 border-slate-200 hover:border-brand-500 hover:text-brand-700',
    subtle: 'bg-slate-100 text-slate-700 border-slate-200 hover:bg-slate-200',
    danger: 'bg-white text-rose-700 border-rose-200 hover:bg-rose-50',
  };

  return (
    <button
      type={type}
      className={`inline-flex min-h-10 items-center justify-center gap-2 rounded-md border px-4 py-2 text-sm font-semibold shadow-sm transition disabled:cursor-not-allowed disabled:opacity-55 ${
        variants[variant] || variants.secondary
      } ${className}`}
      {...props}
    >
      {Icon ? <Icon className="h-4 w-4 shrink-0" aria-hidden="true" /> : null}
      <span className="truncate">{children}</span>
    </button>
  );
}
