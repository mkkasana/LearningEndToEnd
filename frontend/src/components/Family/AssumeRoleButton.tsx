import { UserCheck } from "lucide-react"
import { useState } from "react"

import { Button } from "@/components/ui/button"
import { useActivePersonContext } from "@/contexts/ActivePersonContext"
import useAuth from "@/hooks/useAuth"
import { canAssumeSpecificPerson } from "@/utils/canAssumeRole"

export interface AssumeRoleButtonProps {
  /** The person ID to assume */
  personId: string
  /** The person's display name */
  personName: string
  /** The user ID who created this person */
  createdByUserId: string | null | undefined
  /** Button size variant */
  size?: "sm" | "default"
  /** Additional CSS classes */
  className?: string
}

/**
 * AssumeRoleButton - Allows elevated users to assume a person's role
 * 
 * Only renders if:
 * - User has elevated role (superuser/admin)
 * - User created the person (createdByUserId matches current user)
 * - Not already assuming this person
 * 
 * _Requirements: 6.1, 6.2, 6.4_
 */
export function AssumeRoleButton({
  personId,
  personName,
  createdByUserId,
  size = "sm",
  className,
}: AssumeRoleButtonProps) {
  const { user } = useAuth()
  const { assumePerson, isAssumeLoading, activePersonId } = useActivePersonContext()
  const [isLoading, setIsLoading] = useState(false)

  // Don't render if user can't assume this person
  if (!canAssumeSpecificPerson(user, createdByUserId)) {
    return null
  }

  // Don't render if already viewing as this person
  if (activePersonId === personId) {
    return null
  }

  const handleClick = async (e: React.MouseEvent) => {
    e.stopPropagation() // Prevent card click
    setIsLoading(true)
    try {
      await assumePerson(personId, personName)
    } finally {
      setIsLoading(false)
    }
  }

  const loading = isLoading || isAssumeLoading

  return (
    <Button
      variant="outline"
      size={size}
      className={className}
      onClick={handleClick}
      disabled={loading}
      aria-label={`Assume role of ${personName}`}
    >
      <UserCheck className={size === "sm" ? "h-3 w-3" : "h-4 w-4"} />
      <span className={size === "sm" ? "text-xs" : ""}>
        {loading ? "Assuming..." : "Assume"}
      </span>
    </Button>
  )
}
