package main

import (
	"log"

	"stackguide/backend/internal/handlers"
	"stackguide/backend/internal/server"

	"github.com/gin-gonic/gin"
)

func main() {
	gin.SetMode(gin.ReleaseMode)

	r := server.NewRouter()

	// Routes
	r.GET("/health", handlers.Health)
	r.POST("/upload", handlers.Upload)
	r.GET("/files", handlers.ListFiles)

	if err := r.Run(":8081"); err != nil {
		log.Fatal("Failed to start server:", err)
	}
}
