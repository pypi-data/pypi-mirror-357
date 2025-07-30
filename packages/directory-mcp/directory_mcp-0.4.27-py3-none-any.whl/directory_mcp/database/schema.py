"""Database schema definitions for Directory MCP."""

SCHEMA = """
-- Person: The core entity
CREATE TABLE IF NOT EXISTS person (
    person_id INTEGER PRIMARY KEY AUTOINCREMENT,
    names TEXT NOT NULL,              -- JSON: ["John Doe", "John"]
    email TEXT,                       -- Primary email
    secondary_emails TEXT,            -- JSON: ["john@personal.com"]
    company_id INTEGER,               -- Current employer
    title TEXT,                       -- Job title
    department TEXT,                  -- Department/team
    location TEXT,                    -- City, Country
    timezone TEXT,                    -- e.g., "America/New_York"
    handles TEXT DEFAULT '{}',        -- JSON: {"discord": "john#1234", "slack": "U123"}
    aliases TEXT DEFAULT '[]',        -- JSON: ["JD", "Johnny"]
    bio TEXT,                         -- Short description
    skills TEXT DEFAULT '[]',         -- JSON: ["Python", "AI", "Backend"]
    vector BLOB,                      -- Embedding for all text fields
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (company_id) REFERENCES company(company_id)
);

-- Company: Organizations
CREATE TABLE IF NOT EXISTS company (
    company_id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    domain TEXT,                      -- Primary domain
    domains TEXT DEFAULT '[]',        -- JSON: ["company.com", "company.io"]
    industry TEXT,
    size TEXT,                        -- e.g., "50-200", "1000+"
    location_hq TEXT,                 -- Headquarters
    description TEXT,
    tags TEXT DEFAULT '[]',           -- JSON: ["startup", "AI", "B2B"]
    vector BLOB,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Channel: Communication channels (Slack, Discord, etc.)
CREATE TABLE IF NOT EXISTS channel (
    channel_id INTEGER PRIMARY KEY AUTOINCREMENT,
    platform TEXT NOT NULL,           -- 'slack', 'discord', 'teams', 'email'
    ext_id TEXT NOT NULL,            -- External ID from platform
    name TEXT,
    type TEXT,                       -- 'public', 'private', 'dm', 'group'
    purpose TEXT,                    -- Channel description
    owner_id INTEGER,                -- Person who owns/created it
    company_id INTEGER,              -- Company channel belongs to
    project_id INTEGER,              -- Project channel (optional)
    is_active BOOLEAN DEFAULT TRUE,
    member_count INTEGER,
    vector BLOB,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(platform, ext_id),
    FOREIGN KEY (owner_id) REFERENCES person(person_id),
    FOREIGN KEY (company_id) REFERENCES company(company_id),
    FOREIGN KEY (project_id) REFERENCES project(project_id)
);

-- Project: Work projects/initiatives
CREATE TABLE IF NOT EXISTS project (
    project_id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    code TEXT,                       -- Project code/key (e.g., "PROJ-123")
    description TEXT,
    status TEXT DEFAULT 'active',    -- 'planning', 'active', 'completed', 'archived'
    company_id INTEGER,              -- Which company owns this
    lead_id INTEGER,                 -- Project lead
    start_date DATE,
    end_date DATE,
    tags TEXT DEFAULT '[]',          -- JSON: ["backend", "ai", "priority-high"]
    urls TEXT DEFAULT '{}',          -- JSON: {"github": "...", "jira": "..."}
    vector BLOB,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (company_id) REFERENCES company(company_id),
    FOREIGN KEY (lead_id) REFERENCES person(person_id)
);

-- Email: Email addresses as first-class entities
CREATE TABLE IF NOT EXISTS email (
    email_id INTEGER PRIMARY KEY AUTOINCREMENT,
    address TEXT NOT NULL UNIQUE,
    person_id INTEGER,
    is_primary BOOLEAN DEFAULT FALSE,
    is_verified BOOLEAN DEFAULT FALSE,
    domain TEXT,                     -- Extracted domain
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (person_id) REFERENCES person(person_id)
);

-- Document: Files and documents
CREATE TABLE IF NOT EXISTS document (
    doc_id INTEGER PRIMARY KEY AUTOINCREMENT,
    filename TEXT NOT NULL,
    mime_type TEXT,
    url TEXT,                        -- Where to find it
    description TEXT,
    author_id INTEGER,
    project_id INTEGER,
    company_id INTEGER,
    body_vector BLOB,                -- Separate embedding for document content
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (author_id) REFERENCES person(person_id),
    FOREIGN KEY (project_id) REFERENCES project(project_id),
    FOREIGN KEY (company_id) REFERENCES company(company_id)
);

-- Relationship tables with metadata
CREATE TABLE IF NOT EXISTS person_company (
    person_id INTEGER,
    company_id INTEGER,
    role TEXT,                       -- 'employee', 'contractor', 'advisor'
    start_date DATE,
    end_date DATE,
    is_current BOOLEAN DEFAULT TRUE,
    PRIMARY KEY (person_id, company_id),
    FOREIGN KEY (person_id) REFERENCES person(person_id),
    FOREIGN KEY (company_id) REFERENCES company(company_id)
);

CREATE TABLE IF NOT EXISTS person_channel (
    person_id INTEGER,
    channel_id INTEGER,
    role TEXT,                       -- 'member', 'admin', 'owner'
    joined_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    is_active BOOLEAN DEFAULT TRUE,
    PRIMARY KEY (person_id, channel_id),
    FOREIGN KEY (person_id) REFERENCES person(person_id),
    FOREIGN KEY (channel_id) REFERENCES channel(channel_id)
);

CREATE TABLE IF NOT EXISTS person_project (
    person_id INTEGER,
    project_id INTEGER,
    role TEXT,                       -- 'lead', 'contributor', 'reviewer'
    allocation INTEGER,              -- Percentage allocation
    start_date DATE,
    end_date DATE,
    is_active BOOLEAN DEFAULT TRUE,
    PRIMARY KEY (person_id, project_id),
    FOREIGN KEY (person_id) REFERENCES person(person_id),
    FOREIGN KEY (project_id) REFERENCES project(project_id)
);

-- Indexes for performance
CREATE INDEX IF NOT EXISTS idx_person_company ON person(company_id);
CREATE INDEX IF NOT EXISTS idx_person_email ON person(email);
CREATE INDEX IF NOT EXISTS idx_company_domain ON company(domain);
CREATE INDEX IF NOT EXISTS idx_channel_platform ON channel(platform);
CREATE INDEX IF NOT EXISTS idx_channel_company ON channel(company_id);
CREATE INDEX IF NOT EXISTS idx_channel_project ON channel(project_id);
CREATE INDEX IF NOT EXISTS idx_project_company ON project(company_id);
CREATE INDEX IF NOT EXISTS idx_project_lead ON project(lead_id);
CREATE INDEX IF NOT EXISTS idx_project_status ON project(status);
CREATE INDEX IF NOT EXISTS idx_email_domain ON email(domain);
CREATE INDEX IF NOT EXISTS idx_email_person ON email(person_id);

-- Full-text search indexes
CREATE VIRTUAL TABLE IF NOT EXISTS person_fts USING fts5(
    person_id, names, email, title, department, bio, skills, tokenize='trigram'
);

CREATE VIRTUAL TABLE IF NOT EXISTS company_fts USING fts5(
    company_id, name, domain, industry, description, tags, tokenize='trigram'
);

CREATE VIRTUAL TABLE IF NOT EXISTS channel_fts USING fts5(
    channel_id, name, purpose, platform, tokenize='trigram'
);

CREATE VIRTUAL TABLE IF NOT EXISTS project_fts USING fts5(
    project_id, name, code, description, tags, tokenize='trigram'
);

-- Triggers to maintain FTS indexes
CREATE TRIGGER IF NOT EXISTS person_ai AFTER INSERT ON person BEGIN
    INSERT INTO person_fts(person_id, names, email, title, department, bio, skills) 
    VALUES (new.person_id, new.names, new.email, new.title, new.department, new.bio, new.skills);
END;

CREATE TRIGGER IF NOT EXISTS person_au AFTER UPDATE ON person BEGIN
    UPDATE person_fts SET 
        names = new.names, 
        email = new.email, 
        title = new.title,
        department = new.department,
        bio = new.bio,
        skills = new.skills
    WHERE person_id = new.person_id;
END;

CREATE TRIGGER IF NOT EXISTS person_ad AFTER DELETE ON person BEGIN
    DELETE FROM person_fts WHERE person_id = old.person_id;
END;

CREATE TRIGGER IF NOT EXISTS company_ai AFTER INSERT ON company BEGIN
    INSERT INTO company_fts(company_id, name, domain, industry, description, tags) 
    VALUES (new.company_id, new.name, new.domain, new.industry, new.description, new.tags);
END;

CREATE TRIGGER IF NOT EXISTS company_au AFTER UPDATE ON company BEGIN
    UPDATE company_fts SET 
        name = new.name,
        domain = new.domain,
        industry = new.industry,
        description = new.description,
        tags = new.tags
    WHERE company_id = new.company_id;
END;

CREATE TRIGGER IF NOT EXISTS company_ad AFTER DELETE ON company BEGIN
    DELETE FROM company_fts WHERE company_id = old.company_id;
END;

CREATE TRIGGER IF NOT EXISTS channel_ai AFTER INSERT ON channel BEGIN
    INSERT INTO channel_fts(channel_id, name, purpose, platform) 
    VALUES (new.channel_id, new.name, new.purpose, new.platform);
END;

CREATE TRIGGER IF NOT EXISTS channel_au AFTER UPDATE ON channel BEGIN
    UPDATE channel_fts SET 
        name = new.name,
        purpose = new.purpose,
        platform = new.platform
    WHERE channel_id = new.channel_id;
END;

CREATE TRIGGER IF NOT EXISTS channel_ad AFTER DELETE ON channel BEGIN
    DELETE FROM channel_fts WHERE channel_id = old.channel_id;
END;

CREATE TRIGGER IF NOT EXISTS project_ai AFTER INSERT ON project BEGIN
    INSERT INTO project_fts(project_id, name, code, description, tags) 
    VALUES (new.project_id, new.name, new.code, new.description, new.tags);
END;

CREATE TRIGGER IF NOT EXISTS project_au AFTER UPDATE ON project BEGIN
    UPDATE project_fts SET 
        name = new.name,
        code = new.code,
        description = new.description,
        tags = new.tags
    WHERE project_id = new.project_id;
END;

CREATE TRIGGER IF NOT EXISTS project_ad AFTER DELETE ON project BEGIN
    DELETE FROM project_fts WHERE project_id = old.project_id;
END;

-- Views for common queries
CREATE VIEW IF NOT EXISTS person_details AS
SELECT 
    p.*,
    c.name as company_name,
    c.domain as company_domain,
    COUNT(DISTINCT pch.channel_id) as channel_count,
    COUNT(DISTINCT pp.project_id) as project_count
FROM person p
LEFT JOIN company c ON p.company_id = c.company_id
LEFT JOIN person_channel pch ON p.person_id = pch.person_id
LEFT JOIN person_project pp ON p.person_id = pp.person_id
GROUP BY p.person_id;

CREATE VIEW IF NOT EXISTS channel_details AS
SELECT
    ch.*,
    c.name as company_name,
    p.name as project_name,
    COUNT(DISTINCT pc.person_id) as member_count
FROM channel ch
LEFT JOIN company c ON ch.company_id = c.company_id
LEFT JOIN project p ON ch.project_id = p.project_id
LEFT JOIN person_channel pc ON ch.channel_id = pc.channel_id
GROUP BY ch.channel_id;

CREATE VIEW IF NOT EXISTS project_team AS
SELECT
    p.*,
    pe.names as person_names,
    pe.email as person_email,
    pp.role,
    pp.allocation,
    pp.is_active
FROM project p
LEFT JOIN person_project pp ON p.project_id = pp.project_id
LEFT JOIN person pe ON pp.person_id = pe.person_id;

-- Embedding cache table
CREATE TABLE IF NOT EXISTS embedding_cache (
    cache_id INTEGER PRIMARY KEY AUTOINCREMENT,
    text_hash TEXT NOT NULL UNIQUE,  -- SHA256 of the text
    text TEXT NOT NULL,
    vector BLOB NOT NULL,
    model TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_embedding_cache_hash ON embedding_cache(text_hash);
"""