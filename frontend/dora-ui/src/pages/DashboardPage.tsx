import { useEffect, useState } from "react";
import { Button } from "@/components/ui/button";
import ErrorAlert from "@/components/ErrorAlert";
import DatePicker from "@/components/DatePicker";
import { metrics } from "@/lib/api";
import type { MetricsData } from "@/lib/api";
import { SectionCards } from "@/components/section-cards";
import { ChartAreaInteractive } from "@/components/chart-area-interactive";
import { DataTable } from "@/components/data-table";

const DashboardPage = () => {
  const [metricsData, setMetricsData] = useState<MetricsData | null>(null);
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(true);
  const [startDate, setStartDate] = useState<Date>(
    new Date(Date.now() - 30 * 24 * 60 * 60 * 1000)
  ); // Last 30 days
  const [endDate, setEndDate] = useState<Date>(new Date());

  useEffect(() => {
    fetchMetrics();
  }, [startDate, endDate]);

  const fetchMetrics = async () => {
    try {
      const data = await metrics.get(
        startDate.toISOString().split('T')[0],
        endDate.toISOString().split('T')[0]
      );
      setMetricsData(data);
      setError("");
    } catch (err) {
      setError(
        err instanceof Error ? err.message : "Failed to load metrics data"
      );
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="flex justify-center items-center min-h-[80vh]">
        Loading...
      </div>
    );
  }

  return (
    <div className="flex flex-1 flex-col">
      <div className="@container/main flex flex-1 flex-col gap-2">
        <div className="flex flex-col gap-4 py-4 md:gap-6 md:py-6">
          <div className="flex justify-between items-center px-4 lg:px-6">
            <h1 className="text-2xl font-bold">DORA Metrics Dashboard</h1>
          </div>

          {error && <ErrorAlert message={error} onClose={() => setError('')} />}
          <SectionCards metrics={metricsData} />

          <ChartAreaInteractive />
          
          {/* <DataTable data={data} /> */}
        </div>
      </div>
    </div>
  );
};

export default DashboardPage;
