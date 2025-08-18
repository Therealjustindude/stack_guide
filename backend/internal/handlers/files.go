package handlers

import (
	"net/http"
	"os"
	"path/filepath"
	"strings"

	"stackguide/backend/internal/config"

	"github.com/gin-gonic/gin"
)

// Upload handles POST /upload
func Upload(c *gin.Context) {
	file, err := c.FormFile("file")
	if err != nil {
		c.JSON(http.StatusBadRequest, gin.H{"error": "No file provided"})
		return
	}

	if file.Size > config.MaxFileSize {
		c.JSON(http.StatusBadRequest, gin.H{"error": "File size exceeds the 10MB limit"})
		return
	}

	ext := strings.ToLower(filepath.Ext(file.Filename))
	isAllowed := false
	for _, allowed := range config.AllowedExtensions {
		if ext == allowed {
			isAllowed = true
			break
		}
	}
	if !isAllowed {
		c.JSON(http.StatusBadRequest, gin.H{"error": "File type not supported. Please upload text, markdown, PDF, or data files."})
		return
	}

	uploadDir := config.GetUploadDir()
	if err := os.MkdirAll(uploadDir, 0755); err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{"error": "Failed to create upload directory"})
		return
	}

	filename := filepath.Join(uploadDir, file.Filename)
	if err := c.SaveUploadedFile(file, filename); err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{"error": "Failed to save file"})
		return
	}

	c.JSON(http.StatusOK, gin.H{
		"message":  "File uploaded successfully",
		"filename": file.Filename,
		"size":     file.Size,
	})
}

// ListFiles handles GET /files
func ListFiles(c *gin.Context) {
	uploadDir := config.GetUploadDir()
	entries, err := os.ReadDir(uploadDir)
	if err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{"error": "Failed to read upload directory"})
		return
	}

	files := make([]gin.H, 0)
	for _, e := range entries {
		if e.IsDir() {
			continue
		}
		info, _ := e.Info()
		files = append(files, gin.H{"name": e.Name(), "size": info.Size()})
	}

	c.JSON(http.StatusOK, gin.H{"files": files})
}
