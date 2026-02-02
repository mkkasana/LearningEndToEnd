import { useQuery } from "@tanstack/react-query"
import {
  BarChart3,
  Bug,
  Calendar,
  GitBranch,
  Heart,
  Home,
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

// Workaround for TS6133: explicitly reference icons used in object literals
const ContributionsIcon = BarChart3
const UserApprovalsIcon = UserCheck

const baseItems: Item[] = [
  { icon: Home, title: "Dashboard", path: "/" },
  { icon: UsersRound, title: "Update Family", path: "/family" },
  { icon: Network, title: "Family View", path: "/family-tree" },
  { icon: Share2, title: "Relatives Network", path: "/relatives-network" },
  { icon: Calendar, title: "Life Events", path: "/life-events" },
  { icon: Search, title: "Search", path: "/search" },
  { icon: GitBranch, title: "Rishte", path: "/rishte" },
  { icon: Heart, title: "Find Partner", path: "/find-partner" },
  { icon: ContributionsIcon, title: "My Contributions", path: "/contributions" },
]

// Items that appear after User Approvals
const postApprovalItems: Item[] = [
  { icon: Bug, title: "Report Ticket", path: "/support-tickets" },
]

export function AppSidebar() {
  const { user: currentUser } = useAuth()
  const { isMobile, setOpenMobile } = useSidebar()
  const router = useRouterState()
  const currentPath = router.location.pathname

  // Fetch pending approval count for badge
  // _Requirements: 9.5_
  const { data: pendingCountData } = useQuery({
    queryKey: ["pendingApprovalCount"],
    queryFn: () => AttachmentRequestsService.getPendingCount(),
    refetchInterval: 60000, // Refetch every minute
  })

  const pendingCount = pendingCountData?.count ?? 0

  // Show Admin menu for admin and superuser roles
  const isAdminOrSuperuser =
    currentUser?.role === "admin" || currentUser?.role === "superuser"

  const items = isAdminOrSuperuser
    ? [...baseItems]
    : baseItems

  const finalItems = isAdminOrSuperuser
    ? [...postApprovalItems, { icon: Users, title: "Admin", path: "/admin" }]
    : postApprovalItems

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
        <Main items={items} />
        {/* User Approvals menu item with badge - positioned after My Contributions */}
        {/* _Requirements: 9.1, 9.2, 9.3, 9.4, 9.5_ */}
        <SidebarMenu className="px-2">
          <SidebarMenuItem>
            <SidebarMenuButton
              tooltip="User Approvals"
              isActive={isUserApprovalsActive}
              asChild
            >
              <RouterLink to={"/user-approvals" as any} onClick={handleMenuClick}>
                <UserApprovalsIcon />
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
        <Main items={finalItems} />
      </SidebarContent>
      <SidebarFooter>
        <SidebarAppearance />
        <User user={currentUser} />
      </SidebarFooter>
    </Sidebar>
  )
}

export default AppSidebar
