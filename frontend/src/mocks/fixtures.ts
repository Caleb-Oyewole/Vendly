// src/mocks/fixtures.ts

export const mockEventsList = [
  {
    id: 1,
    name: "Amara's 30th Birthday Gala",
    event_date: "2026-11-14",
    venue: "Eko Hotel, Lagos",
    status: "active",
    vendor_count: 5,
    confirmed_count: 3,
    total_budget: 97500000
  }
];

export const mockEventStatus = {
  changed: true,
  version: 12,
  event: {
    id: 1,
    name: "Amara's 30th Birthday Gala",
    event_date: "2026-11-14",
    start_time: "16:00",
    venue: "Eko Hotel, Lagos",
    status: "active"
  },
  summary: {
    total: 5,
    confirmed: 3,
    sent: 1,
    declined: 1,
    pending: 0,
    failed: 0
  },
  vendors: [
    {
      id: 11,
      role: "DJ",
      name: "Kola Beats",
      phone: "+2348012345671",
      arrival_time: "14:00",
      status: "confirmed",
      status_updated_at: "2026-11-10T14:06:22Z",
      deposit: { amount: 5000000, status: "paid" },
      balance: { amount: 10000000, status: "due" }
    }
  ],
  activity: [
    {
      id: 88,
      type: "vendor_confirmed",
      vendor_id: 11,
      text: "Kola Beats (DJ) confirmed via WhatsApp",
      created_at: "2026-11-10T14:06:22Z"
    }
  ]
};