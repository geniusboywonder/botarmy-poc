# tests/test_database.py
import pytest
import os
import tempfile
from database import DatabaseManager


class TestDatabaseManager:

    def setup_method(self):
        # Create temporary database for testing
        self.db_file = tempfile.NamedTemporaryFile(delete=False)
        self.db = DatabaseManager(self.db_file.name)

    def teardown_method(self):
        # Clean up
        os.unlink(self.db_file.name)

    def test_create_project(self):
        project_id = self.db.create_project("Test Project",
                                            "Test requirements")
        assert project_id is not None

        project = self.db.get_project(project_id)
        assert project["name"] == "Test Project"
        assert project["requirements"] == "Test requirements"

    def test_add_message(self):
        project_id = self.db.create_project("Test", "Test")

        message_id = self.db.add_message(project_id=project_id,
                                         from_agent="analyst",
                                         to_agent="architect",
                                         message_type="handoff",
                                         content={"test": "data"},
                                         confidence=0.8)

        messages = self.db.get_pending_messages("architect")
        assert len(messages) == 1
        assert messages[0]["id"] == message_id
        assert messages[0]["confidence"] == 0.8
