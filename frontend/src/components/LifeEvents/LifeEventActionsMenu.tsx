// @ts-nocheck

import { EllipsisVertical } from "lucide-react"
import { useState } from "react"

import type { LifeEventPublic } from "@/client"
import { Button } from "@/components/ui/button"
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu"
import { DeleteLifeEvent } from "./DeleteLifeEvent"
import { EditLifeEvent } from "./EditLifeEvent"

interface LifeEventActionsMenuProps {
  event: LifeEventPublic
}

export function LifeEventActionsMenu({ event }: LifeEventActionsMenuProps) {
  const [open, setOpen] = useState(false)

  return (
    <DropdownMenu open={open} onOpenChange={setOpen}>
      <DropdownMenuTrigger asChild>
        <Button variant="ghost" size="icon">
          <EllipsisVertical />
        </Button>
      </DropdownMenuTrigger>
      <DropdownMenuContent align="end">
        <EditLifeEvent event={event} onSuccess={() => setOpen(false)} />
        <DeleteLifeEvent
          id={event.id}
          title={event.title}
          onSuccess={() => setOpen(false)}
        />
      </DropdownMenuContent>
    </DropdownMenu>
  )
}
