export function EmptyState({ icon: Icon, title, message, action }) {
  return (
    <div className="rounded-lg border border-dashed border-slate-300 bg-white p-8 text-center">
      {Icon ? (
        <div className="mx-auto flex h-12 w-12 items-center justify-center rounded-md bg-slate-100 text-slate-600">
          <Icon className="h-6 w-6" aria-hidden="true" />
        </div>
      ) : null}
      <h3 className="mt-4 text-base font-bold text-slate-950">{title}</h3>
      {message ? <p className="mx-auto mt-2 max-w-xl text-sm leading-6 text-slate-600">{message}</p> : null}
      {action ? <div className="mt-5">{action}</div> : null}
    </div>
  );
}
