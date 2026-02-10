import { createFileRoute, redirect } from "@tanstack/react-router"

export const Route = createFileRoute("/logout" as any)({
  beforeLoad: async () => {
    // Clear auth token and assumed person state
    localStorage.removeItem("access_token")
    sessionStorage.removeItem("assumedPerson")
    
    // Redirect to login page
    throw redirect({
      to: "/login",
    })
  },
  component: () => null, // Never renders, always redirects
})
