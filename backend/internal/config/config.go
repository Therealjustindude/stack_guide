package config

import (
	"os"
)

const (
	// MaxFileSize defines the maximum allowed upload size in bytes (10MB)
	MaxFileSize int64 = 10 * 1024 * 1024
)

// AllowedExtensions lists the file extensions permitted for upload
var AllowedExtensions = []string{".md", ".txt", ".pdf", ".json", ".csv", ".xml", ".yaml", ".yml"}

// uploadDir holds the current upload directory. It can be overridden in tests
var uploadDir = defaultUploadDir()

func defaultUploadDir() string {
	if v := os.Getenv("STACKGUIDE_UPLOAD_DIR"); v != "" {
		return v
	}
	return "./uploads"
}

// GetUploadDir returns the directory used for uploads
func GetUploadDir() string { return uploadDir }

// SetUploadDir overrides the upload directory (intended for tests)
func SetUploadDir(dir string) { uploadDir = dir }
