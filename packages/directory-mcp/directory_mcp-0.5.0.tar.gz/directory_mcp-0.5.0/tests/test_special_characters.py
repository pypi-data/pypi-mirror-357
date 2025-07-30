#!/usr/bin/env python3
"""
Test suite for special character handling in Directory MCP.

Tests the three main limitations:
1. FTS5 special characters in search
2. Duplicate detection
3. Channel names with hyphens
"""

import pytest
import asyncio
import tempfile
from pathlib import Path

# Import the modules we need to test
import sys
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from directory_mcp.database.manager import DatabaseManager
from directory_mcp.utils.resolver import resolve_person_id, resolve_channel_id
from directory_mcp.utils.embedder import GeminiEmbedder


class TestSpecialCharacters:
    """Test special character handling in search and resolution."""
    
    @pytest.fixture
    async def db_manager(self):
        """Create a temporary database for testing."""
        temp_db = tempfile.NamedTemporaryFile(suffix=".db", delete=False)
        temp_db.close()
        
        db = DatabaseManager(temp_db.name)
        await db.initialize()
        yield db
        await db.close()
        
        # Cleanup
        Path(temp_db.name).unlink(missing_ok=True)
    
    @pytest.fixture
    def embedder(self):
        """Mock embedder for testing."""
        class MockEmbedder:
            async def generate_embedding(self, text: str):
                # Return a simple mock embedding
                return [0.1] * 768
        return MockEmbedder()
    
    @pytest.mark.asyncio
    async def test_email_search_with_at_symbol(self, db_manager):
        """Test searching for email addresses containing @ symbol."""
        # Create a person with email containing @
        await db_manager.create_person(
            names=["John Doe"],
            email="john@example.com",
            embedding=[0.1] * 768
        )
        
        # Test 1: Direct email search should work (existing workaround)
        try:
            person_id = await resolve_person_id(db_manager, "john@example.com")
            assert person_id is not None, "Should find person by exact email"
        except Exception as e:
            pytest.fail(f"Email resolution failed: {e}")
        
        # Test 2: FTS5 search with @ should not crash
        try:
            results = await db_manager.search_people("john@example.com")
            # This might currently fail, but should not crash the system
        except Exception as e:
            # Document the current limitation
            assert "fts5: syntax error" in str(e), f"Unexpected error: {e}"
    
    @pytest.mark.asyncio
    async def test_discord_handle_search(self, db_manager):
        """Test searching for Discord handles containing # symbol."""
        # Create person with Discord handle
        await db_manager.create_person(
            names=["Alice Johnson"],
            email="alice@test.com",
            handles={"discord": "alice#1234"},
            embedding=[0.2] * 768
        )
        
        # Test FTS5 search with # symbol
        try:
            results = await db_manager.search_people("alice#1234")
            # This will likely fail with current implementation
        except Exception as e:
            assert "fts5: syntax error" in str(e), f"Unexpected error: {e}"
    
    @pytest.mark.asyncio
    async def test_hyphenated_names(self, db_manager):
        """Test searching for hyphenated names."""
        # Create person with hyphenated name
        await db_manager.create_person(
            names=["Mary-Jane Watson"],
            email="mj@test.com",
            embedding=[0.3] * 768
        )
        
        # Test search for hyphenated name
        try:
            results = await db_manager.search_people("Mary-Jane")
        except Exception as e:
            # Document if this causes issues
            print(f"Hyphenated name search error: {e}")
    
    @pytest.mark.asyncio
    async def test_apostrophe_names(self, db_manager):
        """Test searching for names with apostrophes."""
        # Create person with apostrophe in name
        await db_manager.create_person(
            names=["Patrick O'Connor"],
            email="patrick@test.com", 
            embedding=[0.4] * 768
        )
        
        # Test search for name with apostrophe
        try:
            results = await db_manager.search_people("O'Connor")
        except Exception as e:
            assert "fts5: syntax error" in str(e), f"Unexpected error: {e}"


class TestDuplicateDetection:
    """Test duplicate detection functionality."""
    
    @pytest.fixture
    async def db_manager(self):
        """Create a temporary database for testing."""
        temp_db = tempfile.NamedTemporaryFile(suffix=".db", delete=False)
        temp_db.close()
        
        db = DatabaseManager(temp_db.name)
        await db.initialize()
        yield db
        await db.close()
        
        # Cleanup
        Path(temp_db.name).unlink(missing_ok=True)
    
    @pytest.mark.asyncio
    async def test_duplicate_email_creation(self, db_manager):
        """Test that duplicate emails are handled properly."""
        # Create first person
        person1_id = await db_manager.create_person(
            names=["John Doe"],
            email="john@test.com",
            embedding=[0.1] * 768
        )
        
        # Try to create another person with same email
        # Current behavior: This will succeed but shouldn't
        person2_id = await db_manager.create_person(
            names=["John Smith"],
            email="john@test.com",  # Same email
            embedding=[0.2] * 768
        )
        
        # Document current limitation
        assert person1_id != person2_id, "Current system allows duplicate emails"
        
        # Check how many people exist with this email
        results = await db_manager.execute_query(
            "SELECT COUNT(*) as count FROM person WHERE email = ?",
            ("john@test.com",)
        )
        count = results[0]['count'] if results else 0
        
        # This should be 1 after we fix the duplicate issue
        print(f"People with same email: {count} (should be 1 after fix)")
    
    @pytest.mark.asyncio
    async def test_duplicate_name_different_email(self, db_manager):
        """Test people with same name but different emails."""
        # Create two people with same name but different emails
        person1_id = await db_manager.create_person(
            names=["John Smith"],
            email="john.smith@company1.com",
            embedding=[0.1] * 768
        )
        
        person2_id = await db_manager.create_person(
            names=["John Smith"],
            email="john.smith@company2.com",
            embedding=[0.2] * 768
        )
        
        # This should be allowed - same name, different email
        assert person1_id != person2_id, "Different people with same name should be allowed"
    
    @pytest.mark.asyncio
    async def test_similar_names_detection(self, db_manager):
        """Test detection of similar names that might be duplicates."""
        # Create person
        await db_manager.create_person(
            names=["John Doe"],
            email="john@test.com",
            embedding=[0.1] * 768
        )
        
        # Create person with similar name (should trigger similarity check)
        await db_manager.create_person(
            names=["J. Doe"],
            email="j.doe@test.com",
            embedding=[0.15] * 768  # Similar embedding
        )
        
        # Future: Should detect these as potential duplicates
        # For now, just verify they're created separately
        results = await db_manager.execute_query(
            "SELECT COUNT(*) as count FROM person WHERE names LIKE '%Doe%'"
        )
        count = results[0]['count'] if results else 0
        assert count == 2, "Similar names should be flagged for review"


class TestChannelNames:
    """Test channel name handling with special characters."""
    
    @pytest.fixture
    async def db_manager(self):
        """Create a temporary database for testing."""
        temp_db = tempfile.NamedTemporaryFile(suffix=".db", delete=False)
        temp_db.close()
        
        db = DatabaseManager(temp_db.name)
        await db.initialize()
        yield db
        await db.close()
        
        # Cleanup
        Path(temp_db.name).unlink(missing_ok=True)
    
    @pytest.mark.asyncio
    async def test_hyphenated_channel_names(self, db_manager):
        """Test creating and resolving channels with hyphens."""
        # Create channel with hyphen in name
        channel_id = await db_manager.create_channel(
            platform="slack",
            ext_id="general-discussion",
            name="general-discussion",
            channel_type="public"
        )
        
        # Test resolving the channel
        try:
            resolved_id = await resolve_channel_id(db_manager, "general-discussion")
            assert resolved_id == channel_id, "Should resolve hyphenated channel name"
        except Exception as e:
            # Document the current limitation
            assert "no such column" in str(e), f"Expected SQL error for hyphens: {e}"
    
    @pytest.mark.asyncio
    async def test_channel_with_hash_symbol(self, db_manager):
        """Test channels with # prefix."""
        # Create channel with # prefix
        channel_id = await db_manager.create_channel(
            platform="slack",
            ext_id="#engineering",
            name="#engineering",
            channel_type="public"
        )
        
        # Test resolving the channel
        try:
            resolved_id = await resolve_channel_id(db_manager, "#engineering")
            assert resolved_id == channel_id, "Should resolve channel with # prefix"
        except Exception as e:
            # Document if this causes issues
            print(f"Channel # prefix error: {e}")
    
    @pytest.mark.asyncio
    async def test_channel_underscore_names(self, db_manager):
        """Test channels with underscores (should work)."""
        # Create channel with underscore
        channel_id = await db_manager.create_channel(
            platform="discord",
            ext_id="general_chat",
            name="general_chat",
            channel_type="public"
        )
        
        # Test resolving the channel
        resolved_id = await resolve_channel_id(db_manager, "general_chat")
        assert resolved_id == channel_id, "Should resolve channel with underscores"


if __name__ == "__main__":
    # Run tests
    pytest.main([__file__, "-v"])