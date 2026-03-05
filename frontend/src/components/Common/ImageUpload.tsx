import { useCallback, useRef, useState } from "react"
import imageCompression from "browser-image-compression"
import { Camera, X } from "lucide-react"
import { cn } from "@/lib/utils"

const ACCEPTED_TYPES = ["image/jpeg", "image/png", "image/webp"]
interface ImageUploadProps {
  value?: File | null
  onChange: (file: File | null) => void
  label?: string
  maxSizeMB?: number
  className?: string
}

export function ImageUpload({
  value,
  onChange,
  label,
  maxSizeMB = 5,
  className,
}: ImageUploadProps) {
  const fileInputRef = useRef<HTMLInputElement>(null)
  const [preview, setPreview] = useState<string | null>(null)
  const [error, setError] = useState<string | null>(null)
  const [isDragging, setIsDragging] = useState(false)
  const [isCompressing, setIsCompressing] = useState(false)

  // Generate preview URL when value changes
  const previewUrl = preview || (value ? URL.createObjectURL(value) : null)

  const validateFile = (file: File): string | null => {
    if (!ACCEPTED_TYPES.includes(file.type)) {
      return "Please select a JPEG, PNG, or WebP image"
    }
    const maxBytes = maxSizeMB * 1024 * 1024
    if (file.size > maxBytes) {
      return `Image must be less than ${maxSizeMB} MB`
    }
    return null
  }

  const processFile = useCallback(
    async (file: File) => {
      setError(null)

      const validationError = validateFile(file)
      if (validationError) {
        setError(validationError)
        return
      }

      setIsCompressing(true)
      try {
        const compressed = await imageCompression(file, {
          maxSizeMB: 1,
          maxWidthOrHeight: 800,
          useWebWorker: true,
          fileType: "image/jpeg",
        })

        const compressedFile = new File([compressed], file.name, {
          type: "image/jpeg",
        })

        const url = URL.createObjectURL(compressedFile)
        setPreview(url)
        onChange(compressedFile)
      } catch {
        setError("Failed to process image. Please try another.")
      } finally {
        setIsCompressing(false)
      }
    },
    [onChange, maxSizeMB],
  )

  const handleClick = () => {
    fileInputRef.current?.click()
  }

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0]
    if (file) processFile(file)
    // Reset input so the same file can be re-selected
    if (fileInputRef.current) fileInputRef.current.value = ""
  }

  const handleDragOver = (e: React.DragEvent) => {
    e.preventDefault()
    e.stopPropagation()
    setIsDragging(true)
  }

  const handleDragLeave = (e: React.DragEvent) => {
    e.preventDefault()
    e.stopPropagation()
    setIsDragging(false)
  }

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault()
    e.stopPropagation()
    setIsDragging(false)

    const file = e.dataTransfer.files?.[0]
    if (file) processFile(file)
  }

  const handleRemove = (e: React.MouseEvent) => {
    e.stopPropagation()
    if (preview) URL.revokeObjectURL(preview)
    setPreview(null)
    setError(null)
    onChange(null)
  }

  return (
    <div className={cn("flex flex-col items-center gap-2", className)}>
      {label && (
        <span className="text-sm font-medium text-foreground">{label}</span>
      )}

      <div
        role="button"
        tabIndex={0}
        aria-label={previewUrl ? "Change profile photo" : "Upload profile photo"}
        onClick={handleClick}
        onKeyDown={(e) => {
          if (e.key === "Enter" || e.key === " ") {
            e.preventDefault()
            handleClick()
          }
        }}
        onDragOver={handleDragOver}
        onDragLeave={handleDragLeave}
        onDrop={handleDrop}
        className={cn(
          "relative flex items-center justify-center rounded-full cursor-pointer transition-all",
          "w-28 h-28 border-2 border-dashed",
          "hover:border-primary/60",
          isDragging
            ? "border-primary bg-primary/10 scale-105"
            : "border-muted-foreground/30 bg-muted/50",
          previewUrl && "border-solid border-transparent",
        )}
      >
        {previewUrl ? (
          <>
            <img
              src={previewUrl}
              alt="Selected profile photo preview"
              className="w-full h-full rounded-full object-cover"
            />
            <button
              type="button"
              onClick={handleRemove}
              aria-label="Remove selected photo"
              className={cn(
                "absolute -top-1 -right-1 rounded-full p-1",
                "bg-destructive text-destructive-foreground shadow-sm",
                "hover:bg-destructive/90 transition-colors",
              )}
            >
              <X className="h-3.5 w-3.5" />
            </button>
          </>
        ) : (
          <div className="flex flex-col items-center gap-1 text-muted-foreground">
            {isCompressing ? (
              <div className="h-8 w-8 animate-spin rounded-full border-2 border-muted-foreground border-t-transparent" />
            ) : (
              <Camera className="h-8 w-8" />
            )}
            <span className="text-xs">
              {isCompressing ? "Processing..." : "Add Photo"}
            </span>
          </div>
        )}
      </div>

      <input
        ref={fileInputRef}
        type="file"
        accept="image/jpeg,image/png,image/webp"
        onChange={handleFileChange}
        className="hidden"
        aria-label="Select profile photo"
      />

      {error && (
        <p className="text-sm text-destructive text-center" role="alert">
          {error}
        </p>
      )}
    </div>
  )
}
