import { cn } from "@/lib/utils"

export interface RowConnectorProps {
  className?: string
}

/**
 * RowConnector component displays a simple downward arrow between family tree rows
 * Provides a visual indicator of generational flow without taking up much space
 * Maximum height of 30px to keep content visible
 * 
 * Requirements: 3.3, 6.2
 */
export function RowConnector({ className }: RowConnectorProps) {
  return (
    <div 
      className={cn(
        "flex items-center justify-center h-[30px] text-muted-foreground/40",
        className
      )}
      aria-hidden="true"
    >
      <span className="text-2xl leading-none">↓</span>
    </div>
  )
}
