"use client";

import * as React from "react";
import { Area, AreaChart, CartesianGrid, XAxis, YAxis } from "recharts";
import { metrics } from "@/lib/api";
import { useIsMobile } from "@/hooks/use-mobile";
import {
    Card,
    CardAction,
    CardContent,
    CardDescription,
    CardHeader,
    CardTitle,
} from "@/components/ui/card";
import {
    ChartConfig,
    ChartContainer,
    ChartTooltip,
    ChartTooltipContent,
} from "@/components/ui/chart";
import {
    Select,
    SelectContent,
    SelectItem,
    SelectTrigger,
    SelectValue,
} from "@/components/ui/select";
import { ToggleGroup, ToggleGroupItem } from "@/components/ui/toggle-group";

export const description = "An interactive area chart";

const chartConfig = {
    Android: {
        label: "Android",
        color: "var(--primary)",
    },
    Samsung: {
        label: "Samsung",
        color: "var(--blue-500)",
    },
    Roku: {
        label: "Roku",
        color: "var(--blue-500)",
    },
    Xbox: {
        label: "Xbox",
        color: "var(--blue-500)",
    },
    PS4: {
        label: "PS4",
        color: "var(--blue-500)",
    },
    PS5: {
        label: "PS5",
        color: "var(--blue-500)",
    },
} satisfies ChartConfig;

export function ChartAreaInteractive() {
    const isMobile = useIsMobile();
    const [timeRange, setTimeRange] = React.useState("90d");
const [selectedPlatform, setSelectedPlatform] = React.useState<string | "Total">("Total");
    const [allData, setAllData] = React.useState<Array<{
        date: string;
        Android?: number;
        Samsung?: number;
        Roku?: number;
        Xbox?: number;
        PS4?: number;
        PS5?: number;
    }>>([]);

    React.useEffect(() => {
        if (isMobile) {
            setTimeRange("7d");
        }
    }, [isMobile]);

    React.useEffect(() => {
        const fetchData = async () => {
            // Get data for last 90 days by default
            const endDate = new Date();
            const startDate = new Date();
            startDate.setDate(startDate.getDate() - 90);

            const data = await metrics.getDeploymentVolume(
                startDate.toISOString().split('T')[0],
                endDate.toISOString().split('T')[0]
            );
            setAllData(data);
        };
        fetchData();
    }, []);

    const filteredData = React.useMemo(() => {
        const referenceDate = new Date();
        let daysToSubtract = 90;
        if (timeRange === "30d") {
            daysToSubtract = 30;
        } else if (timeRange === "7d") {
            daysToSubtract = 7;
        }

        const startDate = new Date(referenceDate);
        startDate.setDate(startDate.getDate() - daysToSubtract);

        const timeFilteredData = allData.filter(item => {
            const date = new Date(item.date);
            return date >= startDate && date <= referenceDate;
        });

        if (selectedPlatform === "Total") {
            // Calculate aggregate for all platforms
            return timeFilteredData.map(item => {
                const total = Object.keys(chartConfig).reduce((sum, platform) => {
                    const value = item[platform as keyof typeof item];
                    return sum + (typeof value === 'number' ? value : 0);
                }, 0);
                return {
                    date: item.date,
                    Total: total
                };
            });
        }

        return timeFilteredData;
    }, [allData, timeRange, selectedPlatform]);

    return (
        <Card className="@container/card">
            <CardHeader>
                <CardTitle>Deployment Volume</CardTitle>
                <CardDescription>
                    <span className="hidden @[540px]/card:block">
                        Number of releases by platform over time
                    </span>
                    <span className="@[540px]/card:hidden">Releases by platform</span>
                </CardDescription>
                <CardAction>
                    <ToggleGroup
                        type="single"
                        value={timeRange}
                        onValueChange={setTimeRange}
                        variant="outline"
                        className="hidden *:data-[slot=toggle-group-item]:!px-4 @[767px]/card:flex"
                    >
                        <ToggleGroupItem value="90d">Last 3 months</ToggleGroupItem>
                        <ToggleGroupItem value="30d">Last 30 days</ToggleGroupItem>
                        <ToggleGroupItem value="7d">Last 7 days</ToggleGroupItem>
                    </ToggleGroup>
                    <Select value={timeRange} onValueChange={setTimeRange}>
                        <SelectTrigger
                            className="flex w-40 **:data-[slot=select-value]:block **:data-[slot=select-value]:truncate @[767px]/card:hidden"
                            size="sm"
                            aria-label="Select a value"
                        >
                            <SelectValue placeholder="Last 3 months" />
                        </SelectTrigger>
                        <SelectContent className="rounded-xl">
                            <SelectItem value="90d" className="rounded-lg">
                                Last 3 months
                            </SelectItem>
                            <SelectItem value="30d" className="rounded-lg">
                                Last 30 days
                            </SelectItem>
                            <SelectItem value="7d" className="rounded-lg">
                                Last 7 days
                            </SelectItem>
                        </SelectContent>
                    </Select>
                </CardAction>
                <div className="mt-4 flex flex-wrap gap-2">
                    {Object.entries(chartConfig).map(([key, config]) => (
                        <button
                            key={key}
                            onClick={() => setSelectedPlatform(key)}
                            className={`rounded px-3 py-1 text-sm transition-colors ${
                                selectedPlatform === key
                                    ? "bg-blue-500 text-white"
                                    : "bg-gray-100 text-gray-600 dark:bg-gray-800 dark:text-gray-400"
                            }`}
                        >
                            {config.label}
                        </button>
                    ))}
                    <button
                        onClick={() => setSelectedPlatform("Total")}
                        className={`rounded px-3 py-1 text-sm transition-colors ${
                            selectedPlatform === "Total"
                                ? "bg-blue-500 text-white"
                                : "bg-gray-100 text-gray-600 dark:bg-gray-800 dark:text-gray-400"
                        }`}
                    >
                        Total
                    </button>
                </div>
            </CardHeader>

            <CardContent className="px-2 pt-4 sm:px-6 sm:pt-6">
                <ChartContainer
                    config={chartConfig}
                    className="aspect-auto h-[250px] w-full"
                >
                    <AreaChart data={filteredData}>
                        <defs>
                            <linearGradient
                                id="fillArea"
                                x1="0"
                                y1="0"
                                x2="0"
                                y2="1"
                            >
                                <stop
                                    offset="5%"
                                    stopColor="var(--color-Android)"
                                    stopOpacity={0.8}
                                />
                                <stop
                                    offset="95%"
                                    stopColor="var(--color-Android)"
                                    stopOpacity={0.1}
                                />
                            </linearGradient>
                        </defs>
                        <CartesianGrid vertical={false} />
                        <XAxis
                            dataKey="date"
                            tickLine={false}
                            axisLine={false}
                            tickMargin={8}
                            minTickGap={32}
                            tickFormatter={(value) => {
                                const date = new Date(value);
                                return date.toLocaleDateString("en-US", {
                                    month: "short",
                                    day: "numeric",
                                });
                            }}
                        />
                        <YAxis
                            label={{
                                value: "Number of Releases",
                                angle: -90,
                                position: "insideLeft",
                                style: { textAnchor: "middle" },
                            }}
                        />
                        <ChartTooltip
                            cursor={false}
                            content={
                                <ChartTooltipContent
                                    labelFormatter={(value) => {
                                        return new Date(value).toLocaleDateString("en-US", {
                                            month: "short",
                                            day: "numeric",
                                        });
                                    }}
                                    indicator="dot"
                                />
                            }
                        />
                        {selectedPlatform === "Total" ? (
                            <Area
                                dataKey="Total"
                                type="monotone"
                                fill="url(#fillArea)"
                                stroke="var(--blue-500)"
                                strokeWidth={2}
                                connectNulls={true}
                                dot={false}
                                activeDot={{ r: 4, strokeWidth: 1}}
                            />
                        ) : (
                            Object.entries(chartConfig)
                                .filter(([key]) => key === selectedPlatform)
                                .map(([key]) => (
                                    <Area
                                        key={key}
                                        dataKey={key}
                                        type="monotone"
                                        fill="url(#fillArea)"
                                        stroke="var(--blue-500)"
                                        strokeWidth={2}
                                        connectNulls={true}
                                        dot={false}
                                        activeDot={{ r: 4, strokeWidth: 1}}
                                    />
                                ))
                        )}
                    </AreaChart>
                </ChartContainer>
            </CardContent>
        </Card>
    );
}
