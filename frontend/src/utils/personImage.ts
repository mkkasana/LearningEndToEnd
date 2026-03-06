export function getPersonImageUrl(
  profileImageKey: string | null | undefined,
  variant: "main" | "thumbnail" = "thumbnail",
): string | undefined {
  if (!profileImageKey) return undefined

  const key =
    variant === "thumbnail"
      ? profileImageKey.replace(/\.jpg$/, "_thumb.jpg")
      : profileImageKey

  // Production: use CloudFront images URL if configured
  const imagesUrl = import.meta.env.VITE_IMAGES_URL
  if (imagesUrl) {
    return `${imagesUrl}/person-images/${key}`
  }

  // Local dev: serve from backend API
  const baseUrl = import.meta.env.VITE_API_URL || ""
  return `${baseUrl}/api/v1/uploads/person-images/${key}`
}
