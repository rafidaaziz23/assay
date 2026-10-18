/**
 * Display timestamps for the demo surfaces.
 *
 * Everything here is computed from the browser clock on purpose. The dossier is the
 * record of the defense that just happened, so a hardcoded date turns a 2026
 * submission into something that reads as a stale mock the moment a judge looks at
 * the audit record.
 */

const MONTHS = [
  'Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun',
  'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec',
] as const;

const pad2 = (n: number): string => String(n).padStart(2, '0');

/** `Oct 18, 2026 • 13:45 UTC` — the audit-record format used by the dossier. */
export function utcTimestamp(date: Date = new Date()): string {
  return (
    `${MONTHS[date.getUTCMonth()]} ${date.getUTCDate()}, ${date.getUTCFullYear()}` +
    ` • ${pad2(date.getUTCHours())}:${pad2(date.getUTCMinutes())} UTC`
  );
}

/** `Aug 06, 2026` — a local-time calendar date, `days` before now. */
export function localDateDaysAgo(days: number, now: Date = new Date()): string {
  const d = new Date(now);
  d.setDate(d.getDate() - days);
  return `${MONTHS[d.getMonth()]} ${d.getDate()}, ${d.getFullYear()}`;
}
