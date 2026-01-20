import {
  Briefcase,
  Bug,
  Calendar,
  GitBranch,
  Heart,
  Home,
  Network,
  Search,
  Users,
  UsersRound,
} from "lucide-react"

import { SidebarAppearance } from "@/components/Common/Appearance"
import { Logo } from "@/components/Common/Logo"
import {
  Sidebar,
  SidebarContent,
  SidebarFooter,
  SidebarHeader,
} from "@/components/ui/sidebar"
import useAuth from "@/hooks/useAuth"
import { type Item, Main } from "./Main"
import { User } from "./User"

const baseItems: Item[] = [
  { icon: Home, title: "Dashboard", path: "/" },
  { icon: Briefcase, title: "Items", path: "/items" },
  { icon: UsersRound, title: "Update Family", path: "/family" },
  { icon: Network, title: "Family View", path: "/family-tree" },
  { icon: Calendar, title: "Life Events", path: "/life-events" },
  { icon: Search, title: "Search", path: "/search" },
  { icon: GitBranch, title: "Rishte", path: "/rishte" },
  { icon: Heart, title: "Find Partner", path: "/find-partner" },
  { icon: Bug, title: "Report Ticket", path: "/support-tickets" },
]

export function AppSidebar() {
  const { user: currentUser } = useAuth()

  // Show Admin menu for admin and superuser roles
  const isAdminOrSuperuser =
    currentUser?.role === "admin" || currentUser?.role === "superuser"

  const items = isAdminOrSuperuser
    ? [...baseItems, { icon: Users, title: "Admin", path: "/admin" }]
    : baseItems

  return (
    <Sidebar collapsible="icon">
      <SidebarHeader className="px-4 py-6 group-data-[collapsible=icon]:px-0 group-data-[collapsible=icon]:items-center">
        <Logo variant="responsive" />
      </SidebarHeader>
      <SidebarContent>
        <Main items={items} />
      </SidebarContent>
      <SidebarFooter>
        <SidebarAppearance />
        <User user={currentUser} />
      </SidebarFooter>
    </Sidebar>
  )
}

export default AppSidebar
