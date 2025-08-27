import Header from "@/components/Header";

export default function SettingsPage() {
  return (
    <div className="min-h-screen bg-gray-100">
      <div className="max-w-7xl mx-auto px-4 py-8">
        <Header />
        <h1 className="text-2xl font-bold">Returns</h1>
        <p className="text-gray-600 mt-2">Manage your settings here.</p>
      </div>
    </div>
  );
}
