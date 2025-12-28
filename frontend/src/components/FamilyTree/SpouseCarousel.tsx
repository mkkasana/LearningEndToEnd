import { useState, memo } from "react"
import { PersonCard } from "./PersonCard"
import { Button } from "@/components/ui/button"
import { ChevronLeft, ChevronRight } from "lucide-react"
import type { PersonDetails } from "@/client"
import { cn } from "@/lib/utils"

export interface SpouseCarouselProps {
  spouses: PersonDetails[]
  onPersonClick: (personId: string) => void
}

/**
 * SpouseCarousel component displays multiple spouses in a carousel/slideshow format
 * with prev/next navigation buttons and indicator dots
 * Performance: Memoized to prevent unnecessary re-renders
 */
export const SpouseCarousel = memo(function SpouseCarousel({ spouses, onPersonClick }: SpouseCarouselProps) {
  const [currentIndex, setCurrentIndex] = useState(0)

  if (spouses.length === 0) {
    return null
  }

  const handlePrevious = () => {
    setCurrentIndex((prev) => (prev === 0 ? spouses.length - 1 : prev - 1))
  }

  const handleNext = () => {
    setCurrentIndex((prev) => (prev === spouses.length - 1 ? 0 : prev + 1))
  }

  const handleDotClick = (index: number) => {
    setCurrentIndex(index)
  }

  const currentSpouse = spouses[currentIndex]

  return (
    <div className="flex flex-col items-center gap-2 md:gap-3">
      <div className="flex items-center gap-1 md:gap-2">
        {/* Previous button */}
        <Button
          variant="outline"
          size="icon"
          onClick={handlePrevious}
          disabled={spouses.length <= 1}
          aria-label="Previous spouse"
          className={cn(
            "h-7 w-7 md:h-8 md:w-8 touch-manipulation",
            "transition-all duration-200",
            "hover:bg-accent hover:scale-110",
            "active:scale-95",
            "disabled:opacity-30 disabled:cursor-not-allowed",
            "focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-primary focus-visible:ring-offset-2"
          )}
        >
          <ChevronLeft className="h-3 w-3 md:h-4 md:w-4" />
        </Button>

        {/* Current spouse card */}
        <div className="transition-all duration-300 ease-in-out">
          <PersonCard
            person={currentSpouse}
            relationshipType="Spouse"
            variant="spouse"
            onClick={onPersonClick}
            showPhoto={true}
          />
        </div>

        {/* Next button */}
        <Button
          variant="outline"
          size="icon"
          onClick={handleNext}
          disabled={spouses.length <= 1}
          aria-label="Next spouse"
          className={cn(
            "h-7 w-7 md:h-8 md:w-8 touch-manipulation",
            "transition-all duration-200",
            "hover:bg-accent hover:scale-110",
            "active:scale-95",
            "disabled:opacity-30 disabled:cursor-not-allowed",
            "focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-primary focus-visible:ring-offset-2"
          )}
        >
          <ChevronRight className="h-3 w-3 md:h-4 md:w-4" />
        </Button>
      </div>

      {/* Indicator dots */}
      {spouses.length > 1 && (
        <div className="flex gap-1 md:gap-1.5" role="tablist" aria-label="Spouse navigation">
          {spouses.map((_, index) => (
            <button
              key={index}
              onClick={() => handleDotClick(index)}
              className={cn(
                "h-1.5 w-1.5 md:h-2 md:w-2 rounded-full transition-all duration-300 ease-in-out",
                "touch-manipulation active:scale-110",
                "min-h-[24px] min-w-[24px] flex items-center justify-center",
                "focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-primary focus-visible:ring-offset-2",
                index === currentIndex
                  ? "bg-primary w-3 md:w-4 shadow-sm"
                  : "bg-muted-foreground/30 hover:bg-muted-foreground/60 hover:scale-125"
              )}
              aria-label={`Go to spouse ${index + 1}`}
              aria-current={index === currentIndex ? "true" : "false"}
              role="tab"
            >
              <span
                className={cn(
                  "h-1.5 w-1.5 md:h-2 md:w-2 rounded-full transition-all duration-300",
                  index === currentIndex
                    ? "bg-primary w-3 md:w-4"
                    : "bg-muted-foreground/30"
                )}
              />
            </button>
          ))}
        </div>
      )}
    </div>
  )
})
