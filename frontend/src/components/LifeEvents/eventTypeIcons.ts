import {
  Baby,
  Heart,
  Cross,
  Home,
  DollarSign,
  Trophy,
  GraduationCap,
  Briefcase,
  Activity,
  Plane,
  Calendar,
  type LucideIcon,
} from "lucide-react"

/**
 * Get the appropriate icon for a life event type
 * @param eventType - The type of life event (birth, marriage, death, etc.)
 * @returns The corresponding Lucide icon component
 */
export function getEventTypeIcon(eventType: string): LucideIcon {
  const iconMap: Record<string, LucideIcon> = {
    birth: Baby,
    marriage: Heart,
    death: Cross,
    purchase: Home,
    sale: DollarSign,
    achievement: Trophy,
    education: GraduationCap,
    career: Briefcase,
    health: Activity,
    travel: Plane,
    other: Calendar,
  }

  return iconMap[eventType] || Calendar
}
