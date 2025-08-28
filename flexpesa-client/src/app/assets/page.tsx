import Header from "@/components/Header";

export default function AssetsPage() {
  return (
    <div className="min-h-screen bg-gray-100">
      <div className="max-w-7xl mx-auto px-4 py-8">
        <Header title="Portfolio Assets" subtitle="Advanced asset analytics and benchmark comparisons"/>
        <p className="text-gray-600 mt-2">Manage your assets here.</p>
      </div>
    </div>
  );
}
