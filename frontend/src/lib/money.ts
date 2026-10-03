export const naira = (kobo: number): string =>
  new Intl.NumberFormat('en-NG', {
    style: 'currency',
    currency: 'NGN',
    maximumFractionDigits: 0,
  }).format(kobo / 100);

export const toKobo = (nairaAmount: number): number => Math.round(nairaAmount * 100);