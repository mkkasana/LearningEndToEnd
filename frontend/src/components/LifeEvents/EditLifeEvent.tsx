// @ts-nocheck

import { Pencil } from "lucide-react"
import { useState } from "react"

import type { LifeEventPublic } from "@/client"
import { DropdownMenuItem } from "@/components/ui/dropdown-menu"
import { EditLifeEventDialog } from "./EditLifeEventDialog"

interface EditLifeEventProps {
  event: LifeEventPublic
  onSuccess: () => void
}

export function EditLifeEvent({ event, onSuccess }: EditLifeEventProps) {
  const [isOpen, setIsOpen] = useState(false)

  const handleSuccess = () => {
    setIsOpen(false)
    onSuccess()
  }

  return (
    <>
      <DropdownMenuItem
        onSelect={(e) => e.preventDefault()}
        onClick={() => setIsOpen(true)}
      >
        <Pencil />
        Edit Event
      </DropdownMenuItem>
      <EditLifeEventDialog
        event={event}
        open={isOpen}
        onOpenChange={setIsOpen}
        onSuccess={handleSuccess}
      />
    </>
  )
}
