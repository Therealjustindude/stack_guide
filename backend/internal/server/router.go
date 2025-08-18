package server

import (
	"log"
	"net/http"

	"github.com/gin-gonic/gin"
)

// NewRouter configures and returns a Gin engine with middleware and routes.
func NewRouter() *gin.Engine {
	gin.SetMode(gin.ReleaseMode)
	r := gin.Default()

	// CORS middleware
	r.Use(func(c *gin.Context) {
		c.Header("Access-Control-Allow-Origin", "*")
		c.Header("Access-Control-Allow-Methods", "GET, POST, PUT, DELETE, OPTIONS")
		c.Header("Access-Control-Allow-Headers", "Origin, Content-Type, Content-Length, Accept-Encoding, X-CSRF-Token, Authorization")
		if c.Request.Method == http.MethodOptions {
			c.AbortWithStatus(http.StatusNoContent)
			return
		}
		c.Next()
	})

	return r
}

// Start runs the HTTP server on the given addr.
func Start(r *gin.Engine, addr string) error {
	log.Println("🚀 Starting Stack Guide Go Backend on", addr)
	log.Println("📊 Health check:", "http://"+addr+"/health")
	log.Println("📁 File upload:", "http://"+addr+"/upload")
	log.Println("📋 List files:", "http://"+addr+"/files")
	return r.Run(":" + addr)
}
