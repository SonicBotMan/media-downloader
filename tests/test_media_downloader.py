#!/usr/bin/env python3
"""
Media Downloader Test Suite v3.2.0
Tests for core functionality without requiring real WebDAV server

Usage:
    python3 tests/test_media_downloader.py
"""

import unittest
import os
import sys
import tempfile
import json
import importlib.util
from unittest.mock import patch, MagicMock

# Mock environment before loading
os.environ['WEBDAV_URL'] = 'http://test.com'
os.environ['WEBDAV_USER'] = 'test'
os.environ['WEBDAV_PASSWORD'] = 'test'

# Load script as module (can't import hyphenated filename directly)
script_path = os.path.join(os.path.dirname(__file__), '..', 'scripts', 'media-downloader.py')
spec = importlib.util.spec_from_file_location("media_downloader", script_path)
media_downloader = importlib.util.module_from_spec(spec)

# Load the module
spec.loader.exec_module(media_downloader)


class TestEnvironmentVariables(unittest.TestCase):
    """Test environment variable requirements"""
    
    def test_required_env_vars_set(self):
        """All required env vars should be set"""
        from media_downloader import WEBDAV_URL, WEBDAV_USER, WEBDAV_PASSWORD
        self.assertIsNotNone(WEBDAV_URL)
        self.assertIsNotNone(WEBDAV_USER)
        self.assertIsNotNone(WEBDAV_PASSWORD)
    
    def test_no_hardcoded_password(self):
        """Password should not be hardcoded"""
        with open('scripts/media-downloader.py', 'r') as f:
            content = f.read()
            # Check no hardcoded password
            self.assertNotIn('He5845211314', content)
            # Check env var is required
            self.assertIn('WEBDAV_PASSWORD', content)


class TestURLDetection(unittest.TestCase):
    """Test URL type detection"""
    
    def test_twitter_url_detection(self):
        """Should detect Twitter/X URLs"""
        from media_downloader import is_twitter_url
        self.assertTrue(is_twitter_url('https://x.com/user/status/123'))
        self.assertTrue(is_twitter_url('https://twitter.com/user/status/123'))
        self.assertFalse(is_twitter_url('https://youtube.com/watch?v=123'))
    
    def test_youtube_url_detection(self):
        """Should detect YouTube URLs"""
        from media_downloader import is_youtube_url
        self.assertTrue(is_youtube_url('https://www.youtube.com/watch?v=123'))
        self.assertTrue(is_youtube_url('https://youtu.be/123'))
        self.assertFalse(is_youtube_url('https://x.com/user/status/123'))
    
    def test_douyin_url_detection(self):
        """Should detect Douyin URLs"""
        from media_downloader import is_douyin_url
        self.assertTrue(is_douyin_url('https://www.douyin.com/video/123'))
        self.assertTrue(is_douyin_url('https://v.douyin.com/abc123'))
        self.assertFalse(is_douyin_url('https://tiktok.com/@user/video/123'))


class TestDeduplication(unittest.TestCase):
    """Test deduplication logic"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.history_file = tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.json')
        self.history_file.write(json.dumps({"urls": {}, "files": {}}))
        self.history_file.close()
    
    def tearDown(self):
        """Clean up test fixtures"""
        if os.path.exists(self.history_file.name):
            os.unlink(self.history_file.name)
    
    @patch('media_downloader.HISTORY_FILE')
    def test_url_dedup(self, mock_history_file):
        """Should detect duplicate URLs"""
        mock_history_file.__str__ = lambda: self.history_file.name
        
        from media_downloader import is_downloaded, mark_downloaded
        
        # First time should not be downloaded
        self.assertFalse(is_downloaded(url='https://example.com/test.jpg'))
        
        # Mark as downloaded
        mark_downloaded(url='https://example.com/test.jpg', webdav_path='/test/test.jpg')
        
        # Second time should be detected
        self.assertTrue(is_downloaded(url='https://example.com/test.jpg'))


class TestFileHash(unittest.TestCase):
    """Test file hash calculation"""
    
    def test_hash_calculation(self):
        """Should calculate MD5 hash correctly"""
        from media_downloader import get_file_hash
        
        # Create temp file with known content
        with tempfile.NamedTemporaryFile(mode='wb', delete=False) as f:
            f.write(b'test content')
            temp_path = f.name
        
        try:
            # Calculate hash
            file_hash = get_file_hash(temp_path)
            self.assertIsNotNone(file_hash)
            self.assertEqual(len(file_hash), 32)  # MD5 hex length
        finally:
            os.unlink(temp_path)
    
    def test_hash_none_on_error(self):
        """Should return None on error"""
        from media_downloader import get_file_hash
        
        # Non-existent file
        file_hash = get_file_hash('/nonexistent/file.jpg')
        self.assertIsNone(file_hash)


class TestTwitterExtraction(unittest.TestCase):
    """Test Twitter media extraction"""
    
    @patch('media_downloader.requests.get')
    def test_extract_twitter_media(self, mock_get):
        """Should extract media URLs from fxtwitter API"""
        # Mock API response
        mock_response = MagicMock()
        mock_response.json.return_value = {
            'code': 200,
            'tweet': {
                'author': {'screen_name': 'testuser'},
                'media': {
                    'all': [
                        {'type': 'photo', 'url': 'https://example.com/image1.jpg'},
                        {'type': 'video', 'url': 'https://example.com/video1.mp4'}
                    ]
                }
            }
        }
        mock_response.raise_for_status = MagicMock()
        mock_get.return_value = mock_response
        
        from media_downloader import get_twitter_media
        urls, author, error = get_twitter_media('https://x.com/testuser/status/123456')
        
        self.assertIsNone(error)
        self.assertEqual(author, 'testuser')
        self.assertEqual(len(urls), 2)
        self.assertEqual(urls[0], ('image', 'https://example.com/image1.jpg'))
        self.assertEqual(urls[1], ('video', 'https://example.com/video1.mp4'))


class TestVersionConsistency(unittest.TestCase):
    """Test version number consistency"""
    
    def test_package_json_version(self):
        """package.json should have correct version"""
        import json
        with open('package.json', 'r') as f:
            pkg = json.load(f)
        self.assertEqual(pkg['version'], '3.2.0')
    
    def test_skill_md_version(self):
        """SKILL.md should have correct version"""
        with open('SKILL.md', 'r') as f:
            content = f.read()
        self.assertIn('version: 3.2.0', content)
    
    def test_script_version_in_comment(self):
        """Script should have version in comment"""
        with open('scripts/media-downloader.py', 'r') as f:
            # Read first 5 lines to find version comment
            lines = [f.readline() for _ in range(5)]
            content = ''.join(lines)
        self.assertIn('v3.2.0', content)


if __name__ == '__main__':
    # Run tests
    unittest.main(verbosity=2)
