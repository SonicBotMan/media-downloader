#!/usr/bin/env python3
"""
Media Downloader Basic Tests v3.2.0
Quick validation tests (no external dependencies)
"""

import unittest
import os
import sys
import json

class TestSecurity(unittest.TestCase):
    """Test security requirements"""
    
    def test_no_hardcoded_password(self):
        """Password should not be hardcoded"""
        script_path = os.path.join(os.path.dirname(__file__), '..', 'scripts', 'media-downloader.py')
        with open(script_path, 'r') as f:
            content = f.read()
        # Check no hardcoded password
        self.assertNotIn('He5845211314', content, "Password should not be hardcoded")
    
    def test_env_var_validation(self):
        """Script should validate required env vars"""
        script_path = os.path.join(os.path.dirname(__file__), '..', 'scripts', 'media-downloader.py')
        with open(script_path, 'r') as f:
            content = f.read()
        # Check env var validation exists
        self.assertIn('WEBDAV_URL', content)
        self.assertIn('WEBDAV_USER', content)
        self.assertIn('WEBDAV_PASSWORD', content)
        self.assertIn('if not all([WEBDAV_URL', content)


class TestVersionConsistency(unittest.TestCase):
    """Test version number consistency"""
    
    def test_package_json_version(self):
        """package.json should have correct version"""
        pkg_path = os.path.join(os.path.dirname(__file__), '..', 'package.json')
        with open(pkg_path, 'r') as f:
            pkg = json.load(f)
        self.assertEqual(pkg['version'], '3.2.0')
    
    def test_skill_md_version(self):
        """SKILL.md should have correct version"""
        skill_path = os.path.join(os.path.dirname(__file__), '..', 'SKILL.md')
        with open(skill_path, 'r') as f:
            content = f.read()
        self.assertIn('version: 3.2.0', content)
    
    def test_script_version_in_comment(self):
        """Script should have version in comment"""
        script_path = os.path.join(os.path.dirname(__file__), '..', 'scripts', 'media-downloader.py')
        with open(script_path, 'r') as f:
            # Read first 5 lines to find version comment
            lines = [f.readline() for _ in range(5)]
            content = ''.join(lines)
        self.assertIn('v3.2.0', content)


class TestCodeStructure(unittest.TestCase):
    """Test code structure"""
    
    def test_skills_directory_removed(self):
        """skills/ directory should be removed"""
        skills_path = os.path.join(os.path.dirname(__file__), '..', 'skills')
        self.assertFalse(os.path.exists(skills_path), "skills/ directory should be removed")
    
    def test_single_entry_point(self):
        """Should have single entry point in scripts/"""
        script_path = os.path.join(os.path.dirname(__file__), '..', 'scripts', 'media-downloader.py')
        self.assertTrue(os.path.exists(script_path), "scripts/media-downloader.py should exist")
    
    def test_changelog_exists(self):
        """CHANGELOG.md should exist"""
        changelog_path = os.path.join(os.path.dirname(__file__), '..', 'CHANGELOG.md')
        self.assertTrue(os.path.exists(changelog_path), "CHANGELOG.md should exist")
    
    def test_release_notes_exists(self):
        """RELEASE_NOTES.md should exist"""
        notes_path = os.path.join(os.path.dirname(__file__), '..', 'RELEASE_NOTES.md')
        self.assertTrue(os.path.exists(notes_path), "RELEASE_NOTES.md should exist")


if __name__ == '__main__':
    # Run tests with verbose output
    unittest.main(verbosity=2)
