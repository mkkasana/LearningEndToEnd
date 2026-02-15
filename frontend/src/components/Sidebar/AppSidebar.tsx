import { useQuery } from "@tanstack/react-query"
import {
  BarChart3,
  Bug,
  Calendar,
  GitBranch,
  Heart,
  Network,
  Search,
  Share2,
  UserCheck,
  Users,
  UsersRound,
} from "lucide-react"

import { AttachmentRequestsService } from "@/client"
import { SidebarAppearance } from "@/components/Common/Appearance"
import { Logo } from "@/components/Common/Logo"
import { Badge } from "@/components/ui/badge"
import {
  Sidebar,
  SidebarContent,
  SidebarFooter,
  SidebarGroup,
  SidebarGroupLabel,
  SidebarHeader,
  SidebarMenu,
  SidebarMenuButton,
  SidebarMenuItem,
  useSidebar,
} from "@/components/ui/sidebar"
import useAuth from "@/hooks/useAuth"
import { type Item, Main } from "./Main"
import { User } from "./User"
import { Link as RouterLink, useRouterState } from "@tanstack/react-router"

// Family section - core family management
const familyItems: Item[] = [
  { icon: Network, title: "Family Tree", path: "/family-tree" },
  { icon: UsersRound, title: "Update Family", path: "/family" },
  { icon: Share2, title: "Relatives Network", path: "/relatives-network" },
  { icon: Calendar, title: "Life Events", path: "/life-events" },
]

// Discovery section - finding and connecting
const discoveryItems: Item[] = [
  { icon: Search, title: "Search", path: "/search" },
  { icon: GitBranch, title: "Rishte", path: "/rishte" },
  { icon: Heart, title: "Find Partner", path: "/find-partner" },
]

// Account section - user-specific
const accountItems: Item[] = [
  { icon: BarChart3, title: "My Contributions", path: "/contributions" },
]

// Support section
const supportItems: Item[] = [
  { icon: Bug, title: "Report Ticket", path: "/support-tickets" },
]

export function AppSidebar() {
  const { user: currentUser } = useAuth()
  const { isMobile, setOpenMobile } = useSidebar()
  const router = useRouterState()
  const currentPath = router.location.pathname

  // Fetch pending approval count for badge
  const { data: pendingCountData } = useQuery({
    queryKey: ["pendingApprovalCount"],
    queryFn: () => AttachmentRequestsService.getPendingCount(),
    refetchInterval: 60000,
  })

  const pendingCount = pendingCountData?.count ?? 0

  // Show Admin menu for admin and superuser roles
  const isAdminOrSuperuser =
    currentUser?.role === "admin" || currentUser?.role === "superuser"

  const handleMenuClick = () => {
    if (isMobile) {
      setOpenMobile(false)
    }
  }

  const isUserApprovalsActive = currentPath === "/user-approvals"

  return (
    <Sidebar collapsible="icon">
      <SidebarHeader className="px-4 py-6 group-data-[collapsible=icon]:px-0 group-data-[collapsible=icon]:items-center">
        <Logo variant="responsive" />
      </SidebarHeader>
      <SidebarContent>
        {/* Family Section */}
        <SidebarGroup>
          <SidebarGroupLabel>Family</SidebarGroupLabel>
          <Main items={familyItems} />
        </SidebarGroup>

        {/* Discovery Section */}
        <SidebarGroup>
          <SidebarGroupLabel>Discover</SidebarGroupLabel>
          <Main items={discoveryItems} />
        </SidebarGroup>

        {/* Account Section */}
        <SidebarGroup>
          <SidebarGroupLabel>Account</SidebarGroupLabel>
          <Main items={accountItems} />
          {/* User Approvals with badge */}
          <SidebarMenu className="px-2">
            <SidebarMenuItem>
              <SidebarMenuButton
                tooltip="User Approvals"
                isActive={isUserApprovalsActive}
                asChild
              >
                <RouterLink to={"/user-approvals" as any} onClick={handleMenuClick}>
                  <UserCheck />
                  <span className="flex items-center gap-2">
                    User Approvals
                    {pendingCount > 0 && (
                      <Badge variant="destructive" className="h-5 min-w-5 px-1.5">
                        {pendingCount}
                      </Badge>
                    )}
                  </span>
                </RouterLink>
              </SidebarMenuButton>
            </SidebarMenuItem>
          </SidebarMenu>
        </SidebarGroup>

        {/* Support & Admin Section */}
        <SidebarGroup>
          <SidebarGroupLabel>Support</SidebarGroupLabel>
          <Main items={supportItems} />
          {isAdminOrSuperuser && (
            <Main items={[{ icon: Users, title: "Admin", path: "/admin" }]} />
          )}
        </SidebarGroup>
      </SidebarContent>
      <SidebarFooter>
        <SidebarAppearance />
        <User user={currentUser} />
      </SidebarFooter>
    </Sidebar>
  )
}

export default AppSidebar
