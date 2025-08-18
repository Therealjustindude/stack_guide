.PHONY: run build test clean

# Run the Go backend
run:
	go run main.go

# Build the Go backend
build:
	go build -o stackguide-backend main.go

# Run tests
test:
	go test ./...

# Clean build artifacts
clean:
	go clean
	rm -f stackguide-backend
	rm -rf uploads

# Install dependencies
deps:
	go mod tidy

# Format code
fmt:
	go fmt ./...

# Lint code
lint:
	golangci-lint run

# Run with hot reload (requires air)
dev:
	air
