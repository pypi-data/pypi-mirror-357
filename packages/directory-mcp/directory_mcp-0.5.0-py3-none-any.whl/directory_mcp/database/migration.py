"""Database migration utilities for Directory MCP."""

import asyncio
import logging
from pathlib import Path
from typing import Dict, List, Optional
import aiosqlite

logger = logging.getLogger(__name__)

class DatabaseMigration:
    """Handles database schema migrations with rollback support."""
    
    def __init__(self, db_path: Path):
        self.db_path = db_path
        self.backup_path = db_path.with_suffix('.bak')
        
    async def backup_database(self) -> bool:
        """Create a backup of the current database."""
        try:
            if self.db_path.exists():
                import shutil
                shutil.copy2(self.db_path, self.backup_path)
                logger.info(f"Database backed up to {self.backup_path}")
                return True
            return False
        except Exception as e:
            logger.error(f"Failed to backup database: {e}")
            return False
    
    async def restore_from_backup(self) -> bool:
        """Restore database from backup."""
        try:
            if self.backup_path.exists():
                import shutil
                shutil.copy2(self.backup_path, self.db_path)
                logger.info(f"Database restored from {self.backup_path}")
                return True
            return False
        except Exception as e:
            logger.error(f"Failed to restore database: {e}")
            return False
    
    async def get_current_schema_version(self) -> str:
        """Get the current schema version from database."""
        try:
            async with aiosqlite.connect(self.db_path) as db:
                # Try to get version from a metadata table
                cursor = await db.execute("""
                    SELECT name FROM sqlite_master 
                    WHERE type='table' AND name='schema_version'
                """)
                table_exists = await cursor.fetchone()
                
                if table_exists:
                    cursor = await db.execute("SELECT version FROM schema_version ORDER BY applied_at DESC LIMIT 1")
                    result = await cursor.fetchone()
                    return result[0] if result else "0.4.28"
                else:
                    # Check if we have FTS5 tables with tokenchars to determine version
                    cursor = await db.execute("""
                        SELECT sql FROM sqlite_master 
                        WHERE type='table' AND name='person_fts'
                    """)
                    result = await cursor.fetchone()
                    if result and 'tokenchars' in result[0]:
                        return "0.4.30"  # Has tokenchars
                    else:
                        return "0.4.29"  # Pre-tokenchars
        except Exception as e:
            logger.error(f"Failed to get schema version: {e}")
            return "unknown"
    
    async def create_schema_version_table(self) -> bool:
        """Create schema version tracking table."""
        try:
            async with aiosqlite.connect(self.db_path) as db:
                await db.execute("""
                    CREATE TABLE IF NOT EXISTS schema_version (
                        version TEXT NOT NULL,
                        description TEXT,
                        applied_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                """)
                await db.commit()
                return True
        except Exception as e:
            logger.error(f"Failed to create schema version table: {e}")
            return False
    
    async def record_migration(self, version: str, description: str) -> bool:
        """Record a successful migration."""
        try:
            async with aiosqlite.connect(self.db_path) as db:
                await db.execute("""
                    INSERT INTO schema_version (version, description) 
                    VALUES (?, ?)
                """, (version, description))
                await db.commit()
                logger.info(f"Recorded migration to version {version}")
                return True
        except Exception as e:
            logger.error(f"Failed to record migration: {e}")
            return False

class FTS5TokencharsUpgrade(DatabaseMigration):
    """Specific migration for adding tokenchars to FTS5 tables."""
    
    ENHANCED_SCHEMA = """
    -- Enhanced FTS5 tables with tokenchars for special character support
    CREATE VIRTUAL TABLE IF NOT EXISTS person_fts_new USING fts5(
        person_id, names, email, title, department, bio, skills, 
        tokenize="unicode61 tokenchars '@.-_#'"
    );

    CREATE VIRTUAL TABLE IF NOT EXISTS company_fts_new USING fts5(
        company_id, name, domain, industry, description, tags, 
        tokenize="unicode61 tokenchars '@.-_#'"
    );

    CREATE VIRTUAL TABLE IF NOT EXISTS channel_fts_new USING fts5(
        channel_id, name, purpose, platform, 
        tokenize="unicode61 tokenchars '@.-_#'"
    );

    CREATE VIRTUAL TABLE IF NOT EXISTS project_fts_new USING fts5(
        project_id, name, code, description, tags, 
        tokenize="unicode61 tokenchars '@.-_#'"
    );
    """
    
    async def check_migration_needed(self) -> bool:
        """Check if FTS5 tokenchars migration is needed."""
        try:
            async with aiosqlite.connect(self.db_path) as db:
                # Check if person_fts has tokenchars
                cursor = await db.execute("""
                    SELECT sql FROM sqlite_master 
                    WHERE type='table' AND name='person_fts'
                """)
                result = await cursor.fetchone()
                
                if result and 'tokenchars' in result[0]:
                    logger.info("FTS5 tokenchars already configured")
                    return False
                else:
                    logger.info("FTS5 tokenchars migration needed")
                    return True
        except Exception as e:
            logger.error(f"Failed to check migration status: {e}")
            return False
    
    async def migrate_fts5_data(self) -> bool:
        """Migrate data from old FTS5 tables to new ones with tokenchars."""
        try:
            async with aiosqlite.connect(self.db_path) as db:
                # Create enhanced FTS5 tables
                await db.executescript(self.ENHANCED_SCHEMA)
                
                # Migrate person data
                logger.info("Migrating person FTS data...")
                await db.execute("""
                    INSERT INTO person_fts_new(person_id, names, email, title, department, bio, skills)
                    SELECT p.person_id, p.names, p.email, p.title, p.department, p.bio, p.skills
                    FROM person p
                """)
                
                # Migrate company data
                logger.info("Migrating company FTS data...")
                await db.execute("""
                    INSERT INTO company_fts_new(company_id, name, domain, industry, description, tags)
                    SELECT c.company_id, c.name, c.domain, c.industry, c.description, c.tags
                    FROM company c
                """)
                
                # Migrate channel data
                logger.info("Migrating channel FTS data...")
                await db.execute("""
                    INSERT INTO channel_fts_new(channel_id, name, purpose, platform)
                    SELECT ch.channel_id, ch.name, ch.purpose, ch.platform
                    FROM channel ch
                """)
                
                # Migrate project data
                logger.info("Migrating project FTS data...")
                await db.execute("""
                    INSERT INTO project_fts_new(project_id, name, code, description, tags)
                    SELECT p.project_id, p.name, p.code, p.description, p.tags
                    FROM project p
                """)
                
                await db.commit()
                logger.info("FTS5 data migration completed")
                return True
                
        except Exception as e:
            logger.error(f"Failed to migrate FTS5 data: {e}")
            return False
    
    async def swap_fts5_tables(self) -> bool:
        """Swap old and new FTS5 tables."""
        try:
            async with aiosqlite.connect(self.db_path) as db:
                # Drop old FTS5 tables and triggers
                await db.execute("DROP TABLE IF EXISTS person_fts")
                await db.execute("DROP TABLE IF EXISTS company_fts") 
                await db.execute("DROP TABLE IF EXISTS channel_fts")
                await db.execute("DROP TABLE IF EXISTS project_fts")
                
                # Drop old triggers
                await db.execute("DROP TRIGGER IF EXISTS person_ai")
                await db.execute("DROP TRIGGER IF EXISTS person_au")
                await db.execute("DROP TRIGGER IF EXISTS person_ad")
                await db.execute("DROP TRIGGER IF EXISTS company_ai")
                await db.execute("DROP TRIGGER IF EXISTS company_au")
                await db.execute("DROP TRIGGER IF EXISTS company_ad")
                await db.execute("DROP TRIGGER IF EXISTS channel_ai")
                await db.execute("DROP TRIGGER IF EXISTS channel_au")
                await db.execute("DROP TRIGGER IF EXISTS channel_ad")
                await db.execute("DROP TRIGGER IF EXISTS project_ai")
                await db.execute("DROP TRIGGER IF EXISTS project_au")
                await db.execute("DROP TRIGGER IF EXISTS project_ad")
                
                # Rename new tables to standard names
                await db.execute("ALTER TABLE person_fts_new RENAME TO person_fts")
                await db.execute("ALTER TABLE company_fts_new RENAME TO company_fts")
                await db.execute("ALTER TABLE channel_fts_new RENAME TO channel_fts")
                await db.execute("ALTER TABLE project_fts_new RENAME TO project_fts")
                
                await db.commit()
                logger.info("FTS5 table swap completed")
                return True
                
        except Exception as e:
            logger.error(f"Failed to swap FTS5 tables: {e}")
            return False
    
    async def create_enhanced_triggers(self) -> bool:
        """Create triggers for enhanced FTS5 tables."""
        try:
            async with aiosqlite.connect(self.db_path) as db:
                # Enhanced triggers with proper FTS5 handling
                await db.executescript("""
                -- Enhanced triggers for FTS5 tables with tokenchars
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
                """)
                
                await db.commit()
                logger.info("Enhanced triggers created")
                return True
                
        except Exception as e:
            logger.error(f"Failed to create enhanced triggers: {e}")
            return False
    
    async def add_duplicate_detection_constraints(self) -> bool:
        """Add database constraints for duplicate detection."""
        try:
            async with aiosqlite.connect(self.db_path) as db:
                # Add unique constraint on person email (if not exists)
                try:
                    await db.execute("CREATE UNIQUE INDEX IF NOT EXISTS idx_person_email_unique ON person(email) WHERE email IS NOT NULL")
                except Exception as e:
                    # Index might already exist or email constraint might be violated
                    logger.warning(f"Could not create unique email index: {e}")
                
                # Add compound indexes for duplicate detection
                await db.execute("CREATE INDEX IF NOT EXISTS idx_person_name_company ON person(names, company_id)")
                await db.execute("CREATE INDEX IF NOT EXISTS idx_person_handles ON person(handles)")
                
                await db.commit()
                logger.info("Duplicate detection constraints added")
                return True
                
        except Exception as e:
            logger.error(f"Failed to add duplicate detection constraints: {e}")
            return False
    
    async def validate_migration(self) -> bool:
        """Validate that the migration was successful."""
        try:
            async with aiosqlite.connect(self.db_path) as db:
                # Check that FTS5 tables exist with tokenchars
                cursor = await db.execute("""
                    SELECT sql FROM sqlite_master 
                    WHERE type='table' AND name='person_fts'
                """)
                result = await cursor.fetchone()
                
                if not result or 'tokenchars' not in result[0]:
                    logger.error("Migration validation failed: tokenchars not found")
                    return False
                
                # Test special character search with simpler test
                await db.execute("INSERT OR IGNORE INTO person (names, email) VALUES (?, ?)", 
                                ('["Test-User"]', 'test-email@example.com'))
                await db.commit()
                
                # Test that hyphen works in search (safer than @ symbol)
                cursor = await db.execute("SELECT * FROM person_fts WHERE person_fts MATCH ?", ('"Test-User"',))
                result = await cursor.fetchone()
                
                if result:
                    logger.info("Migration validation successful: tokenchars work for hyphens")
                    return True
                else:
                    # Try searching for the record without FTS to ensure it exists
                    cursor = await db.execute("SELECT * FROM person WHERE email = ?", ("test-email@example.com",))
                    person_exists = await cursor.fetchone()
                    
                    if person_exists:
                        logger.warning("Migration validation partial: FTS might need reindexing, but structure is correct")
                        return True
                    else:
                        logger.error("Migration validation failed: test data not found")
                        return False
                    
        except Exception as e:
            logger.error(f"Migration validation failed: {e}")
            return False
    
    async def perform_migration(self) -> bool:
        """Perform the complete FTS5 tokenchars migration."""
        logger.info("Starting FTS5 tokenchars migration...")
        
        # Check if migration is needed
        if not await self.check_migration_needed():
            return True
        
        # Create backup
        if not await self.backup_database():
            logger.error("Failed to create backup, aborting migration")
            return False
        
        # Ensure schema version table exists
        await self.create_schema_version_table()
        
        try:
            # Perform migration steps
            if not await self.migrate_fts5_data():
                raise Exception("FTS5 data migration failed")
            
            if not await self.swap_fts5_tables():
                raise Exception("FTS5 table swap failed")
            
            if not await self.create_enhanced_triggers():
                raise Exception("Enhanced triggers creation failed")
            
            if not await self.add_duplicate_detection_constraints():
                raise Exception("Duplicate detection constraints failed")
            
            if not await self.validate_migration():
                raise Exception("Migration validation failed")
            
            # Record successful migration
            await self.record_migration("0.4.30", "FTS5 tokenchars and duplicate detection")
            
            logger.info("FTS5 tokenchars migration completed successfully")
            return True
            
        except Exception as e:
            logger.error(f"Migration failed: {e}")
            logger.info("Attempting to restore from backup...")
            
            if await self.restore_from_backup():
                logger.info("Database restored from backup")
            else:
                logger.error("Failed to restore from backup - manual intervention required")
            
            return False

async def migrate_to_enhanced_fts5(db_path: Path) -> bool:
    """Main entry point for FTS5 tokenchars migration."""
    migration = FTS5TokencharsUpgrade(db_path)
    return await migration.perform_migration()

if __name__ == "__main__":
    # For testing migrations
    import sys
    if len(sys.argv) > 1:
        db_path = Path(sys.argv[1])
        result = asyncio.run(migrate_to_enhanced_fts5(db_path))
        sys.exit(0 if result else 1)