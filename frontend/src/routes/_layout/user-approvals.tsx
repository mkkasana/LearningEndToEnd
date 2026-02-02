/**
 * User Approvals Route
 * 
 * This route displays pending attachment requests for the current user to approve.
 * 
 * _Requirements: 10.1, 10.2, 10.3, 10.5, 10.6_
 */

import { createFileRoute } from "@tanstack/react-router"
import UserApprovalsPage from "@/components/UserApprovals/UserApprovalsPage"

export const Route = createFileRoute("/_layout/user-approvals" as any)({
  component: UserApprovalsPage,
  head: () => ({
    meta: [
      {
        title: "User Approvals - Manage Attachment Requests",
      },
    ],
  }),
})
