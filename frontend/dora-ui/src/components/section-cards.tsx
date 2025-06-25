import { IconTrendingDown, IconTrendingUp, IconAlertCircle } from "@tabler/icons-react"
import { Badge } from "@/components/ui/badge"
import {
  Card,
  CardAction,
  CardDescription,
  CardFooter,
  CardHeader,
  CardTitle,
} from "@/components/ui/card"
import type { MetricsData } from "@/lib/api"

interface SectionCardsProps {
  metrics: MetricsData | null;
}

export function SectionCards({ metrics }: SectionCardsProps) {
  if (!metrics) return null;

  // Helper function to check if a metric is valid
  const isValidMetric = (metricKey: keyof MetricsData) => {
    return metrics[metricKey]?.value !== undefined && 
           metrics[metricKey]?.trend !== undefined;
  };

  const renderMetricCard = (
    title: string,
    metricKey: keyof MetricsData,
    unit: string,
    description: string
  ) => (
      <Card className="@container/card">
        <CardHeader>
          <CardDescription>{title}</CardDescription>
          {isValidMetric(metricKey) ? (
            <>
              <CardTitle className="text-2xl font-semibold tabular-nums @[250px]/card:text-3xl">
                {metrics[metricKey]!.value.toFixed(2)} {unit}
              </CardTitle>
              <CardAction>
                <Badge variant="outline">
                  {metrics[metricKey]!.trend > 0 ? <IconTrendingUp /> : <IconTrendingDown />}
                  {metrics[metricKey]!.trend > 0 ? '+' : ''}{metrics[metricKey]!.trend.toFixed(2)}%
                </Badge>
              </CardAction>
            </>
          ) : (
            <div className="flex flex-col items-start gap-2">
              <CardTitle className="text-muted-foreground">Unable to load data</CardTitle>
              <div className="flex items-center gap-2 text-sm text-muted-foreground">
                <IconAlertCircle className="h-4 w-4" />
                <span>Metric data unavailable</span>
              </div>
            </div>
          )}
        </CardHeader>
        {isValidMetric(metricKey) && (
          <CardFooter className="flex-col items-start gap-1.5 text-sm">
            <div className="line-clamp-1 flex gap-2 font-medium">
              {metrics[metricKey]!.trend > 0 ? 'Trending up' : 'Trending down'} this period{' '}
              {metrics[metricKey]!.trend > 0 ? <IconTrendingUp className="size-4" /> : <IconTrendingDown className="size-4" />}
            </div>
            <div className="text-muted-foreground">{description}</div>
          </CardFooter>
        )}
      </Card>
  );


  return (
    <div className="*:data-[slot=card]:from-primary/5 *:data-[slot=card]:to-card dark:*:data-[slot=card]:bg-card grid grid-cols-1 gap-4 px-4 *:data-[slot=card]:bg-gradient-to-t *:data-[slot=card]:shadow-xs lg:px-0 @xl/main:grid-cols-2 @5xl/main:grid-cols-4">
      {renderMetricCard(
        "Deployment Frequency",
        "deployment_frequency",
        "per day",
        "Compared to previous period"
      )}
      {renderMetricCard(
        "Lead Time for Changes",
        "lead_time",
        "hours",
        "Time from commit to deploy"
      )}
      {renderMetricCard(
        "Time to Restore Service",
        "time_to_restore",
        "hours",
        "Recovery time after failures"
      )}
      {renderMetricCard(
        "Change Failure Rate",
        "change_failure_rate",
        "%",
        "Failed deployments percentage"
      )}
    </div>
  );
}
