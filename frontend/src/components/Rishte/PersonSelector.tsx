import { X } from "lucide-react"
import { useCallback, useState } from "react"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"

/**
 * Props for PersonSelector component (simplified for direct ID input)
 */
export interface PersonSelectorProps {
  label: string // "Person A" or "Person B"
  value: string | null // Currently entered person ID
  onChange: (personId: string | null) => void
  placeholder?: string
}

/**
 * PersonSelector component for entering a person ID directly
 * Simplified version that accepts UUID input for testing purposes
 *
 * Requirements:
 * - 3.1: Display Person_Selector components labeled "Person A" and "Person B"
 * - 3.4: Display the entered person ID when entered
 */
export function PersonSelector({
  label,
  value,
  onChange,
  placeholder = "Enter person ID (UUID)...",
}: PersonSelectorProps) {
  const [inputValue, setInputValue] = useState(value || "")

  const handleInputChange = useCallback(
    (e: React.ChangeEvent<HTMLInputElement>) => {
      const newValue = e.target.value.trim()
      setInputValue(e.target.value)

      // Basic UUID validation (loose check)
      // UUID format: xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx
      const uuidRegex =
        /^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$/i

      if (newValue && uuidRegex.test(newValue)) {
        onChange(newValue)
      } else if (!newValue) {
        onChange(null)
      }
    },
    [onChange],
  )

  const handleClear = useCallback(() => {
    setInputValue("")
    onChange(null)
  }, [onChange])

  const isValidUuid = value !== null

  return (
    <div className="flex flex-col gap-2">
      <Label className="text-sm font-medium">{label}</Label>

      <div className="relative">
        <Input
          type="text"
          placeholder={placeholder}
          value={inputValue}
          onChange={handleInputChange}
          className={isValidUuid ? "pr-10 border-green-500" : ""}
        />
        {inputValue && (
          <Button
            variant="ghost"
            size="sm"
            className="absolute right-1 top-1/2 -translate-y-1/2 h-6 w-6 p-0"
            onClick={handleClear}
            aria-label="Clear input"
          >
            <X className="h-4 w-4" />
          </Button>
        )}
      </div>

      {inputValue && !isValidUuid && (
        <p className="text-xs text-muted-foreground">
          Enter a valid UUID format (e.g., 123e4567-e89b-12d3-a456-426614174000)
        </p>
      )}

      {isValidUuid && (
        <p className="text-xs text-green-600">✓ Valid person ID</p>
      )}
    </div>
  )
}
