import Header from "@/components/Header";

export default function AccountsPage() {
  return (
    <div className="min-h-screen bg-gray-100">
      <div className="max-w-7xl mx-auto px-4 py-8">
        <Header title="Portfolio Accounts" subtitle="Portfolio Account manager"/>
        <h1 className="text-2xl font-bold">Accounts</h1>
        <p className="text-gray-600 mt-2">Manage your linked accounts here.</p>
      </div>
    </div>
  );
}
