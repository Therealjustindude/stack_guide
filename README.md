# Stack Guide - Local-first AI Knowledge Assistant

A modern, modular file upload and management system built with React, Go, and shadcn/ui.

## 🚀 Quick Start (Local Development)

### Prerequisites
- **Node.js** 18+ and npm
- **Go** 1.21+
- **Git**

### 1. Clone and Setup
```bash
git clone <your-repo-url>
cd stack_guide
git checkout feature/restructure-to-go-react-architecture
```

### 2. Start the Go Backend
```bash
cd backend
go run main.go
```
✅ Backend will start on http://localhost:8081

### 3. Start the React Frontend (New Terminal)
```bash
cd frontend
npm install
npm run dev
```
✅ Frontend will start on http://localhost:5173

### 4. Open Your Browser
Navigate to http://localhost:5173 to see the file upload interface!

## 🏗️ Architecture

```
┌─────────────────┐    ┌─────────────────┐
│  React Frontend │    │   Go Backend    │
│   (Port 5173)   │◄──►│   (Port 8081)   │
│     ✅ Ready    │    │     ✅ Ready    │
└─────────────────┘    └─────────────────┘
```

### Frontend (React + TypeScript + Vite)
- **Components**: Modular, focused components (FileUpload, FileList, StatusDisplay)
- **Styling**: Tailwind CSS + shadcn/ui
- **State**: React hooks with clean separation of concerns

### Backend (Go + Gin)
- **Framework**: Gin web framework
- **Endpoints**: Health check, file upload, file listing
- **Storage**: Local file system with uploads directory

## 📁 Project Structure

```
stack_guide/
├── frontend/                 # React application
│   ├── src/
│   │   ├── components/      # Modular UI components
│   │   ├── services/        # API communication layer
│   │   └── App.tsx         # Main application component
│   └── package.json
├── backend/                  # Go server
│   ├── main.go             # Server implementation
│   ├── Makefile            # Go build commands
│   └── uploads/            # File storage directory
└── README.md               # This file
```

## 🧪 Testing the System

### 1. Health Check
```bash
curl http://localhost:8081/health
```

### 2. List Files
```bash
curl http://localhost:8081/files
```

### 3. Upload a File
```bash
curl -X POST -F "file=@test.txt" http://localhost:8081/upload
```

### 4. Web Interface
- Open http://localhost:5173
- Upload files through the UI
- See real-time file listings
- Test error handling with invalid files

## 🔧 Development Commands

### Frontend
```bash
cd frontend
npm run dev          # Start development server
npm run build        # Build for production
npm run preview      # Preview production build
```

### Backend
```bash
cd backend
go run main.go       # Run development server
go build             # Build binary
./stackguide-backend # Run built binary
```

## 🎯 Features

- ✅ **File Upload**: Drag & drop or click to upload
- ✅ **File Validation**: Size limits (10MB) and type checking
- ✅ **Real-time Updates**: File list refreshes automatically
- ✅ **Error Handling**: Clear error messages and validation
- ✅ **Responsive Design**: Works on desktop and mobile
- ✅ **Modular Architecture**: Easy to maintain and extend

## 🚨 Troubleshooting

### Backend Won't Start
- Check if port 8081 is available: `lsof -i :8081`
- Ensure Go is installed: `go version`
- Check Go modules: `go mod tidy`

### Frontend Won't Start
- Check if port 5173 is available: `lsof -i :5173`
- Ensure Node.js is installed: `node --version`
- Reinstall dependencies: `rm -rf node_modules && npm install`

### File Upload Issues
- Check backend is running: `curl http://localhost:8081/health`
- Verify file size is under 10MB
- Check file extension is supported

## 🔮 Next Steps

This is **Spike 4** of the restructure project. Future improvements:
- File deletion and management
- User authentication
- File search and filtering
- AI integration for document analysis
- Containerization for deployment

## 📝 Development Notes

- **Spike 1**: ✅ React frontend setup
- **Spike 2**: ✅ Go backend setup  
- **Spike 3**: ✅ Frontend-backend integration
- **Spike 4**: 🔄 Polish & documentation (current)

---

**Happy coding! 🎉**