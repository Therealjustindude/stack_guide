# Stack Guide Database Schema - Phase 1

## Overview
This document describes the database schema for Stack Guide Phase 1, implementing Role-Based Access Control (RBAC) for documentation management.

## Database Tables

### 1. Users Table
**Purpose**: Store user accounts and roles

```sql
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    email VARCHAR(255) UNIQUE NOT NULL,
    name VARCHAR(255) NOT NULL,
    role VARCHAR(50) NOT NULL DEFAULT 'user' 
        CHECK (role IN ('owner', 'admin', 'manager', 'user')),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);
```

**Columns**:
- `id`: Unique identifier (UUID)
- `email`: User's email address (unique)
- `name`: User's display name
- `role`: User role with constraints
- `created_at`: Account creation timestamp
- `updated_at`: Last update timestamp

**Indexes**:
- Primary key on `id`
- Unique index on `email`
- Performance index on `email`

**Constraints**:
- Role must be one of: 'owner', 'admin', 'manager', 'user'
- Email must be unique

### 2. Documentation Sets Table
**Purpose**: Organize documentation into logical groups

```sql
CREATE TABLE doc_sets (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name VARCHAR(255) NOT NULL,
    description TEXT,
    access_level VARCHAR(50) NOT NULL DEFAULT 'private' 
        CHECK (access_level IN ('public', 'department', 'private')),
    owner_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);
```

**Columns**:
- `id`: Unique identifier (UUID)
- `name`: Documentation set name
- `description`: Optional description
- `access_level`: Access control level
- `owner_id`: User who owns this documentation set
- `created_at`: Creation timestamp
- `updated_at`: Last update timestamp

**Access Levels**:
- `public`: All authenticated users can read
- `department`: Department members + authorized users
- `private`: Only explicitly granted users

### 3. User-Documentation Permissions Table
**Purpose**: Control who can access which documentation

```sql
CREATE TABLE user_doc_permissions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    doc_set_id UUID NOT NULL REFERENCES doc_sets(id) ON DELETE CASCADE,
    permission VARCHAR(50) NOT NULL DEFAULT 'read' 
        CHECK (permission IN ('read', 'write', 'admin')),
    granted_by UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    granted_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    UNIQUE(user_id, doc_set_id)
);
```

**Columns**:
- `id`: Unique identifier (UUID)
- `user_id`: User receiving permission
- `doc_set_id`: Documentation set being accessed
- `permission`: Permission level granted
- `granted_by`: User who granted the permission
- `granted_at`: When permission was granted

**Permissions**:
- `read`: Can view and download files
- `write`: Can upload and delete files
- `admin`: Can manage the documentation set

**Constraints**:
- One permission per user per documentation set
- Cascade delete when user or doc set is removed

### 4. Files Table
**Purpose**: Store uploaded file metadata

```sql
CREATE TABLE files (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name VARCHAR(255) NOT NULL,
    doc_set_id UUID NOT NULL REFERENCES doc_sets(id) ON DELETE CASCADE,
    uploaded_by UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    file_path VARCHAR(500) NOT NULL,
    file_size BIGINT NOT NULL,
    mime_type VARCHAR(100),
    uploaded_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);
```

**Columns**:
- `id`: Unique identifier (UUID)
- `name`: Original filename
- `doc_set_id`: Which documentation set this file belongs to
- `uploaded_by`: User who uploaded the file
- `file_path`: Path to file on filesystem
- `file_size`: File size in bytes
- `mime_type`: File MIME type
- `uploaded_at`: Upload timestamp

## Relationships

```
users (1) ←→ (many) doc_sets
users (1) ←→ (many) user_doc_permissions
doc_sets (1) ←→ (many) user_doc_permissions
doc_sets (1) ←→ (many) files
users (1) ←→ (many) files
```

## Default Data

### Default User
- **ID**: `00000000-0000-0000-0000-000000000001`
- **Email**: `admin@stackguide.local`
- **Name**: `System Administrator`
- **Role**: `owner`

### Default Documentation Sets
1. **Personal Workspace** (private)
2. **Company Handbook** (public)

## Indexes for Performance

```sql
-- User lookups
CREATE INDEX idx_users_email ON users(email);

-- Documentation set lookups
CREATE INDEX idx_doc_sets_owner ON doc_sets(owner_id);

-- Permission lookups
CREATE INDEX idx_user_doc_permissions_user ON user_doc_permissions(user_id);
CREATE INDEX idx_user_doc_permissions_doc ON user_doc_permissions(doc_set_id);

-- File lookups
CREATE INDEX idx_files_doc_set ON files(doc_set_id);
CREATE INDEX idx_files_uploaded_by ON files(uploaded_by);
```

## Security Features

1. **Cascade Deletes**: Removing a user or documentation set removes all related data
2. **Role Constraints**: User roles are restricted to valid values
3. **Permission Granularity**: Fine-grained control over user access
4. **Audit Trail**: Track who granted permissions and when

## Future Enhancements (Phase 2+)

1. **Department Management**: Group users by department
2. **File Versioning**: Track file changes over time
3. **Audit Logging**: Comprehensive access logging
4. **Advanced Permissions**: Time-limited access, conditional permissions
5. **File Sharing**: Direct file sharing between users
