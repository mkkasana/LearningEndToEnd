/**
 * Contributions Page - Route for viewing user's contributions
 * Requirements: 2.1
 *
 * Provides a dedicated page for users to view all persons they have created
 * along with engagement statistics.
 */

import { createFileRoute } from "@tanstack/react-router"
import ContributionsPage from "@/components/Contributions/ContributionsPage"

export const Route = createFileRoute("/_layout/contributions" as any)({
  component: ContributionsPage,
  head: () => ({
    meta: [
      {
        title: "My Contributions - View Your Contributions",
      },
    ],
  }),
})
