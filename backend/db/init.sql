-- Stack Guide Database Schema - Phase 1
-- Initialization script for PostgreSQL

-- Enable UUID extension
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Users table
CREATE TABLE IF NOT EXISTS users (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    email VARCHAR(255) UNIQUE NOT NULL,
    name VARCHAR(255) NOT NULL,
    role VARCHAR(50) NOT NULL DEFAULT 'user' CHECK (role IN ('owner', 'admin', 'manager', 'user')),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Documentation sets table
CREATE TABLE IF NOT EXISTS doc_sets (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name VARCHAR(255) NOT NULL,
    description TEXT,
    access_level VARCHAR(50) NOT NULL DEFAULT 'private' CHECK (access_level IN ('public', 'department', 'private')),
    owner_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- User-documentation permissions table
CREATE TABLE IF NOT EXISTS user_doc_permissions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    doc_set_id UUID NOT NULL REFERENCES doc_sets(id) ON DELETE CASCADE,
    permission VARCHAR(50) NOT NULL DEFAULT 'read' CHECK (permission IN ('read', 'write', 'admin')),
    granted_by UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    granted_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    UNIQUE(user_id, doc_set_id)
);

-- Files table
CREATE TABLE IF NOT EXISTS files (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name VARCHAR(255) NOT NULL,
    doc_set_id UUID NOT NULL REFERENCES doc_sets(id) ON DELETE CASCADE,
    uploaded_by UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    file_path VARCHAR(500) NOT NULL,
    file_size BIGINT NOT NULL,
    mime_type VARCHAR(100),
    uploaded_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Indexes for performance
CREATE INDEX IF NOT EXISTS idx_users_email ON users(email);
CREATE INDEX IF NOT EXISTS idx_doc_sets_owner ON doc_sets(owner_id);
CREATE INDEX IF NOT EXISTS idx_user_doc_permissions_user ON user_doc_permissions(user_id);
CREATE INDEX IF NOT EXISTS idx_user_doc_permissions_doc ON user_doc_permissions(doc_set_id);
CREATE INDEX IF NOT EXISTS idx_files_doc_set ON files(doc_set_id);
CREATE INDEX IF NOT EXISTS idx_files_uploaded_by ON files(uploaded_by);

-- Insert default owner user (will be replaced by actual auth user)
INSERT INTO users (id, email, name, role) 
VALUES (
    '00000000-0000-0000-0000-000000000001',
    'admin@stackguide.local',
    'System Administrator',
    'owner'
) ON CONFLICT (id) DO NOTHING;

-- Insert default documentation sets
INSERT INTO doc_sets (id, name, description, access_level, owner_id)
VALUES 
    (
        '00000000-0000-0000-0000-000000000002',
        'Personal Workspace',
        'Your personal documents and notes',
        'private',
        '00000000-0000-0000-0000-000000000001'
    ),
    (
        '00000000-0000-0000-0000-000000000003',
        'Company Handbook',
        'Company-wide policies and procedures',
        'public',
        '00000000-0000-0000-0000-000000000001'
    )
ON CONFLICT (id) DO NOTHING;

-- Grant permissions for default user
INSERT INTO user_doc_permissions (user_id, doc_set_id, permission, granted_by)
VALUES 
    ('00000000-0000-0000-0000-000000000001', '00000000-0000-0000-0000-000000000002', 'admin', '00000000-0000-0000-0000-000000000001'),
    ('00000000-0000-0000-0000-000000000001', '00000000-0000-0000-0000-000000000003', 'admin', '00000000-0000-0000-0000-000000000001')
ON CONFLICT (user_id, doc_set_id) DO NOTHING;
