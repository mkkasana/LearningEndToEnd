import { useState } from "react"
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
 */
export function SpouseCarousel({ spouses, onPersonClick }: SpouseCarouselProps) {
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
    <div className="flex flex-col items-center gap-3">
      <div className="flex items-center gap-2">
        {/* Previous button */}
        <Button
          variant="outline"
          size="icon"
          onClick={handlePrevious}
          disabled={spouses.length <= 1}
          aria-label="Previous spouse"
          className="h-8 w-8"
        >
          <ChevronLeft className="h-4 w-4" />
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
          className="h-8 w-8"
        >
          <ChevronRight className="h-4 w-4" />
        </Button>
      </div>

      {/* Indicator dots */}
      {spouses.length > 1 && (
        <div className="flex gap-1.5" role="tablist" aria-label="Spouse navigation">
          {spouses.map((_, index) => (
            <button
              key={index}
              onClick={() => handleDotClick(index)}
              className={cn(
                "h-2 w-2 rounded-full transition-all duration-200",
                index === currentIndex
                  ? "bg-primary w-4"
                  : "bg-muted-foreground/30 hover:bg-muted-foreground/50"
              )}
              aria-label={`Go to spouse ${index + 1}`}
              aria-current={index === currentIndex ? "true" : "false"}
              role="tab"
            />
          ))}
        </div>
      )}
    </div>
  )
}
