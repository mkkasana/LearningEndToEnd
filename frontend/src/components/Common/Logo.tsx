import { Link } from "@tanstack/react-router"

import { cn } from "@/lib/utils"

const logoSrc = "/assets/images/manusya-logo.png"

interface LogoProps {
  variant?: "full" | "icon" | "responsive"
  className?: string
  asLink?: boolean
}

export function Logo({
  variant = "full",
  className,
  asLink = true,
}: LogoProps) {
  const content =
    variant === "responsive" ? (
      <span className="flex items-center gap-2">
        <img src={logoSrc} alt="Manusya" className={cn("h-6 w-auto", className)} />
        <span className="font-semibold group-data-[collapsible=icon]:hidden">Manusya</span>
      </span>
    ) : variant === "full" ? (
      <span className="flex items-center gap-2">
        <img src={logoSrc} alt="Manusya" className={cn("h-6 w-auto", className)} />
        <span className="font-semibold">Manusya</span>
      </span>
    ) : (
      <img src={logoSrc} alt="Manusya" className={cn("size-5", className)} />
    )

  if (!asLink) {
    return content
  }

  return <Link to="/">{content}</Link>
}
