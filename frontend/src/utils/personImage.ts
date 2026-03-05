export function getPersonImageUrl(
  profileImageKey: string | null | undefined,
  variant: "main" | "thumbnail" = "thumbnail",
): string | undefined {
  if (!profileImageKey) return undefined

  const key =
    variant === "thumbnail"
      ? profileImageKey.replace(/\.jpg$/, "_thumb.jpg")
      : profileImageKey

  const baseUrl = import.meta.env.VITE_API_URL || ""
  return `${baseUrl}/api/v1/uploads/person-images/${key}`
}
