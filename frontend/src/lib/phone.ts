export function formatPhone(phone: string): string {
  if (!phone) return phone;
  let p = phone.trim();
  if (p.startsWith('0')) {
    p = '+234' + p.substring(1);
  }
  return p;
}
