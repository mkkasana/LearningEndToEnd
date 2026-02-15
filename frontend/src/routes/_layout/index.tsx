import { createFileRoute, redirect } from "@tanstack/react-router"

export const Route = createFileRoute("/_layout/")({
  beforeLoad: () => {
    // Redirect to family-tree as the default landing page
    throw redirect({ to: "/family-tree" })
  },
  component: () => null,
})
