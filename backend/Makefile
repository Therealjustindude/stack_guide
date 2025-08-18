.PHONY: run build test clean test-coverage test-verbose

# Run the Go backend
run:
	go run main.go

# Build the Go backend
build:
	go build -o stackguide-backend main.go

# Run tests
test:
	go test

test-verbose:
	go test -v

test-coverage:
	go test -cover

test-coverage-html:
	go test -coverprofile=coverage.out
	go tool cover -html=coverage.out -o coverage.html

# Clean build artifacts
clean:
	go clean
	rm -f stackguide-backend
	rm -f coverage.out
	rm -f coverage.html
	rm -rf test_uploads

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
