package handlers

import (
	"net/http"

	"github.com/gin-gonic/gin"
)

// Health handles GET /health
func Health(c *gin.Context) {
	c.JSON(http.StatusOK, gin.H{
		"status":  "healthy",
		"service": "stackguide-go-backend",
		"version": "1.0.0",
	})
}
