/**
 * TagInput Component - Multi-select tag input with dropdown
 * Requirements: 5.1, 5.3, 5.4, 5.5, 5.6, 6.1, 6.5, 7.1, 7.5, 8.1, 8.7
 *
 * A reusable component that displays selected items as removable tags
 * and provides a dropdown to add more items from available options.
 */

import { Plus, X } from "lucide-react"
import { Badge } from "@/components/ui/badge"
import { Label } from "@/components/ui/label"
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
} from "@/components/ui/select"
import type { TagInputProps } from "./types"

/**
 * TagInput - Multi-select tag input component
 *
 * Displays selected items as removable badges and provides a dropdown
 * to add new items. The dropdown automatically filters out already
 * selected items.
 */
export function TagInput({
  label,
  selectedItems,
  availableItems,
  onAdd,
  onRemove,
  placeholder = "Add item",
  disabled = false,
}: TagInputProps) {
  // Filter available items to exclude already selected ones
  const unselectedItems = availableItems.filter(
    (item) => !selectedItems.some((selected) => selected.id === item.id)
  )

  // Handle selection from dropdown
  const handleSelect = (itemId: string) => {
    const item = availableItems.find((i) => i.id === itemId)
    if (item) {
      onAdd(item)
    }
  }

  return (
    <div className="space-y-2">
      <Label>{label}</Label>
      <div className="flex flex-wrap gap-2 p-2 border rounded-md min-h-[42px] bg-background">
        {/* Selected tags */}
        {selectedItems.map((item) => (
          <Badge
            key={item.id}
            variant="secondary"
            className="flex items-center gap-1 pr-1"
          >
            <span className="max-w-[150px] truncate">{item.name}</span>
            <button
              type="button"
              onClick={() => onRemove(item.id)}
              disabled={disabled}
              className="ml-1 rounded-full hover:bg-muted-foreground/20 p-0.5 disabled:opacity-50 disabled:cursor-not-allowed"
              aria-label={`Remove ${item.name}`}
            >
              <X className="h-3 w-3" />
            </button>
          </Badge>
        ))}

        {/* Add dropdown - only show if there are unselected items */}
        {unselectedItems.length > 0 && !disabled && (
          <Select onValueChange={handleSelect}>
            <SelectTrigger
              className="w-auto h-7 px-2 border-dashed"
              aria-label={placeholder}
            >
              <Plus className="h-4 w-4" />
            </SelectTrigger>
            <SelectContent>
              {unselectedItems.map((item) => (
                <SelectItem key={item.id} value={item.id}>
                  {item.name}
                </SelectItem>
              ))}
            </SelectContent>
          </Select>
        )}

        {/* Empty state message */}
        {selectedItems.length === 0 && unselectedItems.length === 0 && (
          <span className="text-sm text-muted-foreground">
            No items available
          </span>
        )}
      </div>
    </div>
  )
}
