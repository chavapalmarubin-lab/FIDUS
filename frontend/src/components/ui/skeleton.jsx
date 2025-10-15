import { cn } from "../../lib/utils"

function Skeleton({
  className,
  ...props
}) {
  return (
    <div
      className={cn("animate-pulse rounded-md bg-slate-700/50", className)}
      {...props} />
  );
}

// PHASE 4: Specialized skeleton components
function ChartSkeleton({ height = 300, className = "" }) {
  return (
    <div className={cn("space-y-4", className)}>
      <div className="flex justify-between items-center">
        <Skeleton className="h-6 w-1/3" />
        <Skeleton className="h-8 w-1/5" />
      </div>
      <Skeleton className="rounded-lg" style={{ height: `${height}px` }} />
      <div className="flex gap-4 justify-center">
        <Skeleton className="h-4 w-20" />
        <Skeleton className="h-4 w-20" />
        <Skeleton className="h-4 w-20" />
      </div>
    </div>
  );
}

function MetricCardSkeleton({ className = "" }) {
  return (
    <div className={cn("p-6 space-y-3", className)}>
      <div className="flex items-center gap-2">
        <Skeleton className="h-10 w-10 rounded-full" />
        <Skeleton className="h-5 w-1/2" />
      </div>
      <Skeleton className="h-9 w-2/3" />
      <Skeleton className="h-4 w-2/5" />
    </div>
  );
}

function TableSkeleton({ rows = 5, className = "" }) {
  return (
    <div className={cn("space-y-2", className)}>
      <Skeleton className="h-10 w-full" />
      {Array.from({ length: rows }).map((_, i) => (
        <Skeleton key={i} className="h-16 w-full" />
      ))}
    </div>
  );
}

export { Skeleton, ChartSkeleton, MetricCardSkeleton, TableSkeleton }
