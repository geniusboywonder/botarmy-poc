export default function Logs({ logs, logsEndRef }) {
  return (
    <div className="space-y-6">
      <h2 className="text-2xl font-bold bg-clip-text text-transparent bg-gradient-to-r from-slate-700 to-slate-900 dark:from-slate-100 dark:to-slate-300">
        Logs (JSONL)
      </h2>
      <div className="bg-black text-green-400 rounded-xl p-4 font-mono text-sm h-96 overflow-y-auto">
        {logs.slice(-200).map((line, i) => (
          <div key={i}>{line}</div>
        ))}
        <div ref={logsEndRef} />
      </div>
    </div>
  );
}
