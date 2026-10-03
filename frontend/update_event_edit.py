import os

dashboard_patch = """
  const [isEditSlideOpen, setIsEditSlideOpen] = useState(false);
  const { register: registerEvent, handleSubmit: handleEventSubmit } = useForm();

  const onEditEvent = async (data: any) => {
    try {
      await api.patch(`/events/${eventId}`, data);
      setToastMessage('Event updated successfully');
      setIsEditSlideOpen(false);
      refetch();
    } catch (e) {
      setToastMessage('Failed to update event');
    }
  };
"""

with open('src/pages/EventDashboardPage.tsx', 'r', encoding='utf-8') as f:
    dashboard = f.read()

# Add states
dashboard = dashboard.replace(
    "  const [isAddingVendor, setIsAddingVendor] = useState(false);",
    "  const [isAddingVendor, setIsAddingVendor] = useState(false);\n" + dashboard_patch
)

# Replace alert with state
dashboard = dashboard.replace(
    "onClick={() => alert('Edit Event slide is under construction')}",
    "onClick={() => setIsEditSlideOpen(true)}"
)

# Add Slide-over UI
slide_over_ui = """
      {/* Event Edit Slide-over */}
      {isEditSlideOpen && (
        <>
          <div className="fixed inset-0 bg-ink/30 z-40 transition-opacity backdrop-blur-sm" onClick={() => setIsEditSlideOpen(false)} />
          <div className="fixed inset-y-0 right-0 z-50 w-full max-w-md bg-surface shadow-2xl overflow-y-auto border-l border-line p-6">
            <div className="flex justify-between items-center mb-6">
              <h2 className="text-xl font-bold text-ink">Edit Event</h2>
              <button onClick={() => setIsEditSlideOpen(false)} className="text-muted hover:text-ink text-2xl font-light">&times;</button>
            </div>
            <form onSubmit={handleEventSubmit(onEditEvent)} className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-ink mb-1">Event Name</label>
                <input {...registerEvent('name')} defaultValue={event.name} className="w-full rounded-input border border-line px-3 py-2 text-sm" required />
              </div>
              <div>
                <label className="block text-sm font-medium text-ink mb-1">Date</label>
                <input {...registerEvent('event_date')} type="date" defaultValue={event.event_date} className="w-full rounded-input border border-line px-3 py-2 text-sm" required />
              </div>
              <div>
                <label className="block text-sm font-medium text-ink mb-1">Time</label>
                <input {...registerEvent('start_time')} type="time" defaultValue={event.start_time} className="w-full rounded-input border border-line px-3 py-2 text-sm" required />
              </div>
              <div>
                <label className="block text-sm font-medium text-ink mb-1">Venue</label>
                <input {...registerEvent('venue')} defaultValue={event.venue} className="w-full rounded-input border border-line px-3 py-2 text-sm" required />
              </div>
              <div className="pt-4 flex justify-end gap-3">
                <button type="button" onClick={() => setIsEditSlideOpen(false)} className="px-4 py-2 text-sm border rounded">Cancel</button>
                <button type="submit" className="px-4 py-2 text-sm bg-brand text-white rounded">Save Changes</button>
              </div>
            </form>
          </div>
        </>
      )}

"""

# Inject before {selectedVendor && ...}
dashboard = dashboard.replace("{selectedVendor && (", slide_over_ui + "      {selectedVendor && (")

with open('src/pages/EventDashboardPage.tsx', 'w', encoding='utf-8') as f:
    f.write(dashboard)


with open('src/mocks/mockApi.ts', 'r', encoding='utf-8') as f:
    mock_api = f.read()

patch_api = """    if (path.match(/^\\/events\\/\\d+$/)) {
      statusState.event = { ...statusState.event, ...data };
      statusState.version += 1;
      return statusState.event;
    }
"""
mock_api = mock_api.replace("await delay(300);\n", "await delay(300);\n" + patch_api)

with open('src/mocks/mockApi.ts', 'w', encoding='utf-8') as f:
    f.write(mock_api)

print("Added Event Edit Slide")
