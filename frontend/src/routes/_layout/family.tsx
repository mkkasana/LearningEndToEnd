import { createFileRoute } from "@tanstack/react-router"
import { Users } from "lucide-react"
import { useState } from "react"
import { Button } from "@/components/ui/button"
import { AddFamilyMemberDialog } from "@/components/Family/AddFamilyMemberDialog"

export const Route = createFileRoute("/_layout/family" as any)({
  component: Family,
})

function Family() {
  const [showAddDialog, setShowAddDialog] = useState(false)

  return (
    <div className="flex flex-col gap-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold tracking-tight">Update Family</h1>
          <p className="text-muted-foreground">
            Add and manage your family members
          </p>
        </div>
        <Button onClick={() => setShowAddDialog(true)}>
          <Users className="mr-2 h-4 w-4" />
          Add Family Member
        </Button>
      </div>

      <div className="flex flex-col items-center justify-center text-center py-12 border rounded-lg">
        <div className="rounded-full bg-muted p-4 mb-4">
          <Users className="h-8 w-8 text-muted-foreground" />
        </div>
        <h3 className="text-lg font-semibold">No family members yet</h3>
        <p className="text-muted-foreground mb-4">
          Add your first family member to get started
        </p>
        <Button onClick={() => setShowAddDialog(true)}>
          Add Family Member
        </Button>
      </div>

      <AddFamilyMemberDialog
        open={showAddDialog}
        onOpenChange={setShowAddDialog}
      />
    </div>
  )
}
