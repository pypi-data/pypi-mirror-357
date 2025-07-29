"""Tests for utility functions in afcli"""

import pytest
from datetime import datetime
from afcli import format_datetime, get_status_color


class TestFormatDatetime:
    """Test the format_datetime utility function"""
    
    @pytest.mark.unit
    def test_format_datetime_valid_iso_string(self):
        """Test formatting a valid ISO datetime string"""
        dt_str = "2024-01-15T14:30:00Z"
        result = format_datetime(dt_str)
        assert result == "2024-01-15 14:30:00"
    
    @pytest.mark.unit
    def test_format_datetime_with_timezone(self):
        """Test formatting datetime with timezone"""
        dt_str = "2024-01-15T14:30:00+00:00"
        result = format_datetime(dt_str)
        assert result == "2024-01-15 14:30:00"
    
    @pytest.mark.unit
    def test_format_datetime_with_microseconds(self):
        """Test formatting datetime with microseconds"""
        dt_str = "2024-01-15T14:30:00.123456Z"
        result = format_datetime(dt_str)
        assert result == "2024-01-15 14:30:00"
    
    @pytest.mark.unit
    def test_format_datetime_none(self):
        """Test formatting None datetime"""
        result = format_datetime(None)
        assert result == "N/A"
    
    @pytest.mark.unit
    def test_format_datetime_empty_string(self):
        """Test formatting empty string"""
        result = format_datetime("")
        assert result == "N/A"
    
    @pytest.mark.unit
    def test_format_datetime_invalid_format(self):
        """Test formatting invalid datetime string"""
        dt_str = "invalid-datetime"
        result = format_datetime(dt_str)
        # Should return the original string if parsing fails
        assert result == "invalid-datetime"


class TestGetStatusColor:
    """Test the get_status_color utility function"""
    
    @pytest.mark.unit
    def test_get_status_color_success(self):
        """Test color for success status"""
        from afcli import Fore
        result = get_status_color("success")
        assert result == Fore.GREEN
    
    @pytest.mark.unit
    def test_get_status_color_failed(self):
        """Test color for failed status"""
        from afcli import Fore
        result = get_status_color("failed")
        assert result == Fore.RED
    
    @pytest.mark.unit
    def test_get_status_color_running(self):
        """Test color for running status"""
        from afcli import Fore
        result = get_status_color("running")
        assert result == Fore.YELLOW
    
    @pytest.mark.unit
    def test_get_status_color_queued(self):
        """Test color for queued status"""
        from afcli import Fore
        result = get_status_color("queued")
        assert result == Fore.CYAN
    
    @pytest.mark.unit
    def test_get_status_color_scheduled(self):
        """Test color for scheduled status"""
        from afcli import Fore
        result = get_status_color("scheduled")
        assert result == Fore.BLUE
    
    @pytest.mark.unit
    def test_get_status_color_skipped(self):
        """Test color for skipped status"""
        from afcli import Fore
        result = get_status_color("skipped")
        assert result == Fore.MAGENTA
    
    @pytest.mark.unit
    def test_get_status_color_case_insensitive(self):
        """Test that status color matching is case insensitive"""
        from afcli import Fore
        result = get_status_color("SUCCESS")
        assert result == Fore.GREEN
        
        result = get_status_color("Failed")
        assert result == Fore.RED
    
    @pytest.mark.unit
    def test_get_status_color_unknown_status(self):
        """Test color for unknown status"""
        from afcli import Fore
        result = get_status_color("unknown_status")
        assert result == Fore.WHITE
    
    @pytest.mark.unit
    def test_get_status_color_up_for_retry(self):
        """Test color for up_for_retry status"""
        from afcli import Fore
        result = get_status_color("up_for_retry")
        assert result == Fore.YELLOW
    
    @pytest.mark.unit
    def test_get_status_color_deferred(self):
        """Test color for deferred status"""
        from afcli import Fore
        result = get_status_color("deferred")
        assert result == Fore.CYAN
    
    @pytest.mark.unit
    def test_get_status_color_removed(self):
        """Test color for removed status"""
        from afcli import Fore
        result = get_status_color("removed")
        assert result == Fore.LIGHTBLACK_EX