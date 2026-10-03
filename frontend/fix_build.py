import os
import re

files = {
    "src/components/StatCard.tsx": """interface StatCardProps {
  label: string;
  value: number | string;
  valueColor?: string;
  prefix?: string;
  isMoney?: boolean;
}

export default function StatCard({ label, value, valueColor = "text-ink", prefix = "", isMoney = false }: StatCardProps) {
  let displayValue = value;
  if (isMoney && typeof value === 'number') {
     displayValue = (value / 100).toLocaleString();
  }
  return (
    <div className="rounded-card border border-line bg-white p-4 shadow-sm">
      <span className="text-xs font-medium text-muted block mb-1">{label}</span>
      <div className={`text-2xl font-semibold ${valueColor}`}>{prefix}{displayValue}</div>
    </div>
  );
}
""",
}

for filepath, content in files.items():
    with open(filepath, 'w') as f:
        f.write(content)

with open('src/mocks/mockApi.ts', 'r') as f:
    mock_api = f.read()
    
mock_api = mock_api.replace("pendingVendor.status = 'confirmed';", "const oldStatus = pendingVendor.status;\\n             pendingVendor.status = 'confirmed';")
mock_api = mock_api.replace("if (pendingVendor.status === 'sent')", "if (oldStatus === 'sent')")
mock_api = mock_api.replace("if (pendingVendor.status === 'pending')", "if (oldStatus === 'pending')")

with open('src/mocks/mockApi.ts', 'w') as f:
    f.write(mock_api)

with open('src/pages/EventDashboardPage.tsx', 'r') as f:
    dashboard = f.read()

dashboard = dashboard.replace("const [isEditSlideOpen, setIsEditSlideOpen] = useState(false);\\n", "")
dashboard = dashboard.replace("onClick={() => setIsEditSlideOpen(true)}", "onClick={() => alert('Edit Event slide is under construction')}")

with open('src/pages/EventDashboardPage.tsx', 'w') as f:
    f.write(dashboard)
print("Files updated")
