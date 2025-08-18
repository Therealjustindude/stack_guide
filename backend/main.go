package main

import (
	"log"
	"net/http"
	"os"
	"path/filepath"

	"github.com/gin-gonic/gin"
)

func main() {
	// Set Gin to release mode for production
	gin.SetMode(gin.ReleaseMode)

	// Create a new Gin router
	r := gin.Default()

	// Add CORS middleware
	r.Use(func(c *gin.Context) {
		c.Header("Access-Control-Allow-Origin", "*")
		c.Header("Access-Control-Allow-Methods", "GET, POST, PUT, DELETE, OPTIONS")
		c.Header("Access-Control-Allow-Headers", "Origin, Content-Type, Content-Length, Accept-Encoding, X-CSRF-Token, Authorization")

		if c.Request.Method == "OPTIONS" {
			c.AbortWithStatus(204)
			return
		}

		c.Next()
	})

	// Health check endpoint
	r.GET("/health", func(c *gin.Context) {
		c.JSON(http.StatusOK, gin.H{
			"status":  "healthy",
			"service": "stackguide-go-backend",
			"version": "1.0.0",
		})
	})

	// Basic file upload endpoint
	r.POST("/upload", func(c *gin.Context) {
		file, err := c.FormFile("file")
		if err != nil {
			c.JSON(http.StatusBadRequest, gin.H{
				"error": "No file provided",
			})
			return
		}

		// Create uploads directory if it doesn't exist
		uploadDir := "./uploads"
		if err := os.MkdirAll(uploadDir, 0755); err != nil {
			c.JSON(http.StatusInternalServerError, gin.H{
				"error": "Failed to create upload directory",
			})
			return
		}

		// Save the file
		filename := filepath.Join(uploadDir, file.Filename)
		if err := c.SaveUploadedFile(file, filename); err != nil {
			c.JSON(http.StatusInternalServerError, gin.H{
				"error": "Failed to save file",
			})
			return
		}

		c.JSON(http.StatusOK, gin.H{
			"message":  "File uploaded successfully",
			"filename": file.Filename,
			"size":     file.Size,
		})
	})

	// List uploaded files
	r.GET("/files", func(c *gin.Context) {
		uploadDir := "./uploads"
		files, err := os.ReadDir(uploadDir)
		if err != nil {
			c.JSON(http.StatusInternalServerError, gin.H{
				"error": "Failed to read upload directory",
			})
			return
		}

		var fileList []gin.H
		for _, file := range files {
			if !file.IsDir() {
				info, _ := file.Info()
				fileList = append(fileList, gin.H{
					"name": file.Name(),
					"size": info.Size(),
				})
			}
		}

		c.JSON(http.StatusOK, gin.H{
			"files": fileList,
		})
	})

	// Start the server on port 8081
	log.Println("🚀 Starting Stack Guide Go Backend on port 8081...")
	log.Println("📊 Health check: http://localhost:8081/health")
	log.Println("📁 File upload: http://localhost:8081/upload")
	log.Println("📋 List files: http://localhost:8081/files")

	if err := r.Run(":8081"); err != nil {
		log.Fatal("Failed to start server:", err)
	}
}
