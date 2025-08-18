package main

import (
	"bytes"
	"encoding/json"
	"fmt"
	"mime/multipart"
	"net/http"
	"net/http/httptest"
	"os"
	"path/filepath"
	"testing"

	"stackguide/backend/internal/config"
	"stackguide/backend/internal/handlers"
	"stackguide/backend/internal/server"

	"github.com/gin-gonic/gin"
	"github.com/stretchr/testify/assert"
)

func setupTestRouter() *gin.Engine {
	gin.SetMode(gin.TestMode)
	// Use a dedicated test uploads directory
	config.SetUploadDir("./test_uploads")

	r := server.NewRouter()
	r.GET("/health", handlers.Health)
	r.POST("/upload", handlers.Upload)
	r.GET("/files", handlers.ListFiles)
	return r
}

func cleanupTestFiles() {
	os.RemoveAll("./test_uploads")
}

func TestHealthEndpoint(t *testing.T) {
	defer cleanupTestFiles()

	r := setupTestRouter()
	w := httptest.NewRecorder()
	req, _ := http.NewRequest("GET", "/health", nil)
	r.ServeHTTP(w, req)

	assert.Equal(t, http.StatusOK, w.Code)

	var response map[string]interface{}
	err := json.Unmarshal(w.Body.Bytes(), &response)
	assert.NoError(t, err)

	assert.Equal(t, "healthy", response["status"])
	assert.Equal(t, "stackguide-go-backend", response["service"])
	assert.Equal(t, "1.0.0", response["version"])
}

func TestFileUploadValidFile(t *testing.T) {
	defer cleanupTestFiles()

	r := setupTestRouter()

	// Create a test file
	testContent := "This is a test file content"
	testFile := "test_upload.txt"
	err := os.WriteFile(testFile, []byte(testContent), 0644)
	assert.NoError(t, err)
	defer os.Remove(testFile)

	// Create multipart form
	body := &bytes.Buffer{}
	writer := multipart.NewWriter(body)
	part, err := writer.CreateFormFile("file", testFile)
	assert.NoError(t, err)

	fileContent, err := os.ReadFile(testFile)
	assert.NoError(t, err)
	_, _ = part.Write(fileContent)
	_ = writer.Close()

	// Make request
	w := httptest.NewRecorder()
	req, _ := http.NewRequest("POST", "/upload", body)
	req.Header.Set("Content-Type", writer.FormDataContentType())
	r.ServeHTTP(w, req)

	assert.Equal(t, http.StatusOK, w.Code)

	var response map[string]interface{}
	err = json.Unmarshal(w.Body.Bytes(), &response)
	assert.NoError(t, err)

	assert.Equal(t, "File uploaded successfully", response["message"])
	assert.Equal(t, testFile, response["filename"])
	assert.Equal(t, float64(len(testContent)), response["size"])
}

func TestFileUploadFileTooLarge(t *testing.T) {
	defer cleanupTestFiles()

	r := setupTestRouter()

	// Create a file larger than configured limit
	largeContent := make([]byte, config.MaxFileSize+1024)
	testFile := "large_test.bin"
	err := os.WriteFile(testFile, largeContent, 0644)
	assert.NoError(t, err)
	defer os.Remove(testFile)

	// Create multipart form
	body := &bytes.Buffer{}
	writer := multipart.NewWriter(body)
	part, err := writer.CreateFormFile("file", testFile)
	assert.NoError(t, err)
	_, _ = part.Write(largeContent)
	_ = writer.Close()

	// Make request
	w := httptest.NewRecorder()
	req, _ := http.NewRequest("POST", "/upload", body)
	req.Header.Set("Content-Type", writer.FormDataContentType())
	r.ServeHTTP(w, req)

	assert.Equal(t, http.StatusBadRequest, w.Code)

	var response map[string]interface{}
	err = json.Unmarshal(w.Body.Bytes(), &response)
	assert.NoError(t, err)

	assert.Equal(t, "File size exceeds the 10MB limit", response["error"])
}

func TestFileUploadInvalidFileType(t *testing.T) {
	defer cleanupTestFiles()

	r := setupTestRouter()

	// Create a file with invalid extension
	testContent := "This is a test executable"
	testFile := "test.exe"
	err := os.WriteFile(testFile, []byte(testContent), 0644)
	assert.NoError(t, err)
	defer os.Remove(testFile)

	// Create multipart form
	body := &bytes.Buffer{}
	writer := multipart.NewWriter(body)
	part, err := writer.CreateFormFile("file", testFile)
	assert.NoError(t, err)
	_, _ = part.Write([]byte(testContent))
	_ = writer.Close()

	// Make request
	w := httptest.NewRecorder()
	req, _ := http.NewRequest("POST", "/upload", body)
	req.Header.Set("Content-Type", writer.FormDataContentType())
	r.ServeHTTP(w, req)

	assert.Equal(t, http.StatusBadRequest, w.Code)

	var response map[string]interface{}
	err = json.Unmarshal(w.Body.Bytes(), &response)
	assert.NoError(t, err)

	assert.Equal(t, "File type not supported. Please upload text, markdown, PDF, or data files.", response["error"])
}

func TestFileUploadNoFile(t *testing.T) {
	defer cleanupTestFiles()

	r := setupTestRouter()

	// Make request without file
	w := httptest.NewRecorder()
	req, _ := http.NewRequest("POST", "/upload", nil)
	r.ServeHTTP(w, req)

	assert.Equal(t, http.StatusBadRequest, w.Code)

	var response map[string]interface{}
	err := json.Unmarshal(w.Body.Bytes(), &response)
	assert.NoError(t, err)

	assert.Equal(t, "No file provided", response["error"])
}

func TestFilesEndpointEmpty(t *testing.T) {
	defer cleanupTestFiles()

	r := setupTestRouter()

	// Ensure test_uploads directory exists but is empty
	testDir := "./test_uploads"
	err := os.MkdirAll(testDir, 0755)
	assert.NoError(t, err)

	// Verify directory was created
	_, err = os.Stat(testDir)
	assert.NoError(t, err)

	w := httptest.NewRecorder()
	req, _ := http.NewRequest("GET", "/files", nil)
	r.ServeHTTP(w, req)

	assert.Equal(t, http.StatusOK, w.Code)

	var response map[string]interface{}
	err = json.Unmarshal(w.Body.Bytes(), &response)
	assert.NoError(t, err)

	// Check that files field exists and is an array
	filesField, exists := response["files"]
	assert.True(t, exists, "Response should contain 'files' field")

	// The files field should be an empty array, not nil
	assert.NotNil(t, filesField, "Files field should not be nil")

	files, ok := filesField.([]interface{})
	assert.True(t, ok, "Files field should be an array")
	assert.Len(t, files, 0, "Files array should be empty")
}

func TestFilesEndpointWithFiles(t *testing.T) {
	defer cleanupTestFiles()

	r := setupTestRouter()

	// Create test uploads directory and files
	testDir := "./test_uploads"
	err := os.MkdirAll(testDir, 0755)
	assert.NoError(t, err)

	// Create test files
	testFiles := map[string]string{
		"test1.txt":  "Content 1",
		"test2.md":   "Content 2",
		"test3.json": `{"key": "value"}`,
	}

	for filename, content := range testFiles {
		p := filepath.Join(testDir, filename)
		err := os.WriteFile(p, []byte(content), 0644)
		assert.NoError(t, err)
	}

	// Make request
	w := httptest.NewRecorder()
	req, _ := http.NewRequest("GET", "/files", nil)
	r.ServeHTTP(w, req)

	assert.Equal(t, http.StatusOK, w.Code)

	var response map[string]interface{}
	err = json.Unmarshal(w.Body.Bytes(), &response)
	assert.NoError(t, err)

	files, ok := response["files"].([]interface{})
	assert.True(t, ok)
	assert.Len(t, files, 3)

	// Check that all test files are present
	fileNames := make(map[string]bool)
	for _, file := range files {
		fileMap, ok := file.(map[string]interface{})
		assert.True(t, ok)
		name, ok := fileMap["name"].(string)
		assert.True(t, ok)
		fileNames[name] = true
	}

	for expectedFile := range testFiles {
		assert.True(t, fileNames[expectedFile], fmt.Sprintf("Expected file %s not found", expectedFile))
	}
}

func TestCORSHeaders(t *testing.T) {
	defer cleanupTestFiles()

	r := setupTestRouter()
	w := httptest.NewRecorder()
	req, _ := http.NewRequest("GET", "/health", nil)
	r.ServeHTTP(w, req)

	assert.Equal(t, "*", w.Header().Get("Access-Control-Allow-Origin"))
	assert.Equal(t, "GET, POST, PUT, DELETE, OPTIONS", w.Header().Get("Access-Control-Allow-Methods"))
}

func TestOptionsRequest(t *testing.T) {
	defer cleanupTestFiles()

	r := setupTestRouter()
	w := httptest.NewRecorder()
	req, _ := http.NewRequest("OPTIONS", "/health", nil)
	r.ServeHTTP(w, req)

	assert.Equal(t, http.StatusNoContent, w.Code)
}

func TestFileUploadValidFileTypes(t *testing.T) {
	defer cleanupTestFiles()

	r := setupTestRouter()

	validExtensions := []string{".txt", ".md", ".pdf", ".json", ".csv", ".xml", ".yaml", ".yml"}

	for _, ext := range validExtensions {
		t.Run(fmt.Sprintf("ValidExtension_%s", ext), func(t *testing.T) {
			// Create test file with valid extension
			testContent := "Test content"
			testFile := "test" + ext
			err := os.WriteFile(testFile, []byte(testContent), 0644)
			assert.NoError(t, err)
			defer os.Remove(testFile)

			// Create multipart form
			body := &bytes.Buffer{}
			writer := multipart.NewWriter(body)
			part, err := writer.CreateFormFile("file", testFile)
			assert.NoError(t, err)
			_, _ = part.Write([]byte(testContent))
			_ = writer.Close()

			// Make request
			w := httptest.NewRecorder()
			req, _ := http.NewRequest("POST", "/upload", body)
			req.Header.Set("Content-Type", writer.FormDataContentType())
			r.ServeHTTP(w, req)

			assert.Equal(t, http.StatusOK, w.Code, "Failed for extension: %s", ext)

			var response map[string]interface{}
			err = json.Unmarshal(w.Body.Bytes(), &response)
			assert.NoError(t, err)

			assert.Equal(t, "File uploaded successfully", response["message"])
		})
	}
}
