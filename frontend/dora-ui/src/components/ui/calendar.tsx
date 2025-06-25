"use client"

import * as React from "react"
import { ChevronLeft, ChevronRight } from "lucide-react"

import { cn } from "@/lib/utils"
import { Button } from "@/components/ui/button"

export type CalendarProps = Omit<React.HTMLAttributes<HTMLDivElement>, 'onSelect'> & {
  selected?: Date
  onSelect?: (date: Date | undefined) => void
  disabled?: (date: Date) => boolean
  defaultMonth?: Date
}

function Calendar({
  className,
  selected,
  onSelect,
  disabled,
  defaultMonth,
  ...props
}: CalendarProps) {
  const today = new Date()
  const [currentMonth, setCurrentMonth] = React.useState(defaultMonth || today)
  const [selectedDate, setSelectedDate] = React.useState<Date | undefined>(selected)

  React.useEffect(() => {
    setSelectedDate(selected)
  }, [selected])

  const daysInMonth = new Date(
    currentMonth.getFullYear(),
    currentMonth.getMonth() + 1,
    0
  ).getDate()

  const firstDayOfMonth = new Date(
    currentMonth.getFullYear(),
    currentMonth.getMonth(),
    1
  ).getDay()

  const handleDateSelect = (date: Date) => {
    if (disabled?.(date)) return

    setSelectedDate(date)
    onSelect?.(date)
  }

  const days = Array.from({ length: daysInMonth }, (_, i) => i + 1)

  return (
    <div className={cn("p-3", className)} {...props}>
      <div className="space-y-4">
        <div className="flex items-center justify-between">
          <Button
            type="button"
            variant="ghost"
            onClick={() =>
              setCurrentMonth(
                new Date(currentMonth.getFullYear(), currentMonth.getMonth() - 1)
              )
            }
          >
            <ChevronLeft className="h-4 w-4" />
          </Button>
          <div className="font-medium">
            {currentMonth.toLocaleString("default", {
              month: "long",
              year: "numeric",
            })}
          </div>
          <Button
            type="button"
            variant="ghost"
            onClick={() =>
              setCurrentMonth(
                new Date(currentMonth.getFullYear(), currentMonth.getMonth() + 1)
              )
            }
          >
            <ChevronRight className="h-4 w-4" />
          </Button>
        </div>
        <div className="grid grid-cols-7 text-center text-sm">
          {["Sun", "Mon", "Tue", "Wed", "Thu", "Fri", "Sat"].map((day) => (
            <div key={day} className="text-muted-foreground">
              {day}
            </div>
          ))}
        </div>
        <div className="grid grid-cols-7 gap-1 text-sm">
          {Array.from({ length: firstDayOfMonth }).map((_, index) => (
            <div key={`empty-${index}`} />
          ))}
          {days.map((day) => {
            const date = new Date(
              currentMonth.getFullYear(),
              currentMonth.getMonth(),
              day
            )
            const isSelected =
              selectedDate?.toDateString() === date.toDateString()
            const isToday = today.toDateString() === date.toDateString()
            const isDisabled = disabled?.(date)

            return (
              <Button
                key={day}
                type="button"
                variant="ghost"
                className={cn(
                  "h-8 w-8 p-0 font-normal",
                  isSelected && "bg-primary text-primary-foreground",
                  isToday && "bg-accent text-accent-foreground",
                  isDisabled && "text-muted-foreground opacity-50"
                )}
                disabled={isDisabled}
                onClick={() => handleDateSelect(date)}
              >
                {day}
              </Button>
            )
          })}
        </div>
      </div>
    </div>
  )
}
Calendar.displayName = "Calendar"

export { Calendar }
