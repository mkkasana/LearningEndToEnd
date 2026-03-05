import { useState } from "react"
import { Loader2 } from "lucide-react"
import { Button } from "@/components/ui/button"
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card"
import { ImageUpload } from "@/components/Common/ImageUpload"
import useCustomToast from "@/hooks/useCustomToast"

interface ProfilePhotoStepProps {
  onComplete: () => void
  onSkip: () => void
}

export function ProfilePhotoStep({ onComplete, onSkip }: ProfilePhotoStepProps) {
  const [file, setFile] = useState<File | null>(null)
  const [isUploading, setIsUploading] = useState(false)
  const { showErrorToast } = useCustomToast()

  const handleUpload = async () => {
    if (!file) return

    setIsUploading(true)
    try {
      const token = localStorage.getItem("access_token")
      const apiBase = import.meta.env.VITE_API_URL || ""
      const formData = new FormData()
      formData.append("file", file)

      const response = await fetch(
        `${apiBase}/api/v1/person/me/profile-image`,
        {
          method: "POST",
          headers: { Authorization: `Bearer ${token}` },
          body: formData,
        },
      )

      if (!response.ok) {
        throw new Error("Upload failed")
      }

      onComplete()
    } catch {
      showErrorToast("Failed to upload profile photo. Please try again.")
    } finally {
      setIsUploading(false)
    }
  }

  return (
    <Card className="w-full max-w-md mx-auto">
      <CardHeader className="text-center">
        <CardTitle>Add a Profile Photo</CardTitle>
        <CardDescription>
          Upload a photo so your family members can recognize you. You can skip
          this and add one later.
        </CardDescription>
      </CardHeader>
      <CardContent className="flex flex-col items-center gap-6">
        <ImageUpload value={file} onChange={setFile} />
        <div className="flex w-full gap-3">
          <Button
            variant="outline"
            className="flex-1"
            onClick={onSkip}
            disabled={isUploading}
          >
            Skip
          </Button>
          <Button
            className="flex-1"
            onClick={handleUpload}
            disabled={!file || isUploading}
          >
            {isUploading && <Loader2 className="animate-spin" />}
            {isUploading ? "Uploading..." : "Upload & Continue"}
          </Button>
        </div>
      </CardContent>
    </Card>
  )
}
