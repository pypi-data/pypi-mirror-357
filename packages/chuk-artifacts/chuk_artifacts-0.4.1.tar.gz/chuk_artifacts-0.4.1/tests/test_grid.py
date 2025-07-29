# -*- coding: utf-8 -*-
# tests/test_grid_improved.py
"""
Tests for the improved chuk_artifacts.grid module.

Tests grid-style path utilities with strict validation.
"""

import pytest
from chuk_artifacts.grid import (
    canonical_prefix, artifact_key, parse,
    is_valid_grid_key, validate_grid_key, GridError, _ROOT
)


class TestGridError:
    """Test the GridError exception."""
    
    def test_grid_error_inheritance(self):
        """Test that GridError inherits from ValueError."""
        assert issubclass(GridError, ValueError)
        
        # Should be usable as ValueError
        try:
            raise GridError("test error")
        except ValueError as e:
            assert str(e) == "test error"
    
    def test_grid_error_message(self):
        """Test GridError with custom message."""
        error = GridError("Custom error message")
        assert str(error) == "Custom error message"


class TestValidateComponent:
    """Test the _validate_component helper function."""
    
    def test_validate_component_valid(self):
        """Test validation with valid components."""
        from chuk_artifacts.grid import _validate_component
        
        # These should not raise
        _validate_component("valid-id", "test_component")
        _validate_component("123", "test_component")
        _validate_component("a", "test_component")
        _validate_component("sandbox_with_underscores", "test_component")
        _validate_component("sandbox-with-dashes", "test_component")
    
    def test_validate_component_empty_string(self):
        """Test validation with empty string."""
        from chuk_artifacts.grid import _validate_component
        
        with pytest.raises(GridError) as exc_info:
            _validate_component("", "test_component")
        
        assert "test_component cannot be empty" in str(exc_info.value)
    
    def test_validate_component_non_string(self):
        """Test validation with non-string types."""
        from chuk_artifacts.grid import _validate_component
        
        invalid_types = [None, 123, [], {}, object()]
        
        for invalid_input in invalid_types:
            with pytest.raises(GridError) as exc_info:
                _validate_component(invalid_input, "test_component")
            
            assert "must be a string" in str(exc_info.value)
    
    def test_validate_component_with_slash(self):
        """Test validation with slash characters."""
        from chuk_artifacts.grid import _validate_component
        
        invalid_components = [
            "sandbox/with/slashes",
            "component/",
            "/component",
            "comp/onent"
        ]
        
        for component in invalid_components:
            with pytest.raises(GridError) as exc_info:
                _validate_component(component, "test_component")
            
            assert "cannot contain '/' characters" in str(exc_info.value)


class TestCanonicalPrefix:
    """Test the canonical_prefix function with validation."""
    
    def test_canonical_prefix_valid(self):
        """Test canonical prefix with valid inputs."""
        result = canonical_prefix("sandbox1", "session1")
        assert result == "grid/sandbox1/session1/"
    
    def test_canonical_prefix_special_characters(self):
        """Test canonical prefix with valid special characters."""
        result = canonical_prefix("sandbox-123", "session_456")
        assert result == "grid/sandbox-123/session_456/"
    
    def test_canonical_prefix_empty_sandbox(self):
        """Test canonical prefix with empty sandbox."""
        with pytest.raises(GridError) as exc_info:
            canonical_prefix("", "session1")
        
        assert "sandbox_id cannot be empty" in str(exc_info.value)
    
    def test_canonical_prefix_empty_session(self):
        """Test canonical prefix with empty session."""
        with pytest.raises(GridError) as exc_info:
            canonical_prefix("sandbox1", "")
        
        assert "session_id cannot be empty" in str(exc_info.value)
    
    def test_canonical_prefix_sandbox_with_slash(self):
        """Test canonical prefix with slash in sandbox."""
        with pytest.raises(GridError) as exc_info:
            canonical_prefix("sandbox/with/slash", "session1")
        
        assert "cannot contain '/' characters" in str(exc_info.value)
    
    def test_canonical_prefix_session_with_slash(self):
        """Test canonical prefix with slash in session."""
        with pytest.raises(GridError) as exc_info:
            canonical_prefix("sandbox1", "session/with/slash")
        
        assert "cannot contain '/' characters" in str(exc_info.value)
    
    def test_canonical_prefix_non_string_inputs(self):
        """Test canonical prefix with non-string inputs."""
        with pytest.raises(GridError):
            canonical_prefix(123, "session1")
        
        with pytest.raises(GridError):
            canonical_prefix("sandbox1", None)


class TestArtifactKey:
    """Test the artifact_key function with validation."""
    
    def test_artifact_key_valid(self):
        """Test artifact key with valid inputs."""
        result = artifact_key("sandbox1", "session1", "artifact1")
        assert result == "grid/sandbox1/session1/artifact1"
    
    def test_artifact_key_special_characters(self):
        """Test artifact key with valid special characters."""
        result = artifact_key("sandbox-1", "session_2", "artifact.3")
        assert result == "grid/sandbox-1/session_2/artifact.3"
    
    def test_artifact_key_empty_sandbox(self):
        """Test artifact key with empty sandbox."""
        with pytest.raises(GridError) as exc_info:
            artifact_key("", "session1", "artifact1")
        
        assert "sandbox_id cannot be empty" in str(exc_info.value)
    
    def test_artifact_key_empty_session(self):
        """Test artifact key with empty session."""
        with pytest.raises(GridError) as exc_info:
            artifact_key("sandbox1", "", "artifact1")
        
        assert "session_id cannot be empty" in str(exc_info.value)
    
    def test_artifact_key_empty_artifact(self):
        """Test artifact key with empty artifact."""
        with pytest.raises(GridError) as exc_info:
            artifact_key("sandbox1", "session1", "")
        
        assert "artifact_id cannot be empty" in str(exc_info.value)
    
    def test_artifact_key_with_slashes(self):
        """Test artifact key with slashes in components."""
        with pytest.raises(GridError):
            artifact_key("sandbox/1", "session1", "artifact1")
        
        with pytest.raises(GridError):
            artifact_key("sandbox1", "session/1", "artifact1")
        
        with pytest.raises(GridError):
            artifact_key("sandbox1", "session1", "artifact/1")
    
    def test_artifact_key_non_string_inputs(self):
        """Test artifact key with non-string inputs."""
        with pytest.raises(GridError):
            artifact_key(123, "session1", "artifact1")
        
        with pytest.raises(GridError):
            artifact_key("sandbox1", 456, "artifact1")
        
        with pytest.raises(GridError):
            artifact_key("sandbox1", "session1", 789)


class TestParseStrict:
    """Test the improved parse function with strict validation."""
    
    def test_parse_valid_basic(self):
        """Test parsing valid basic key."""
        key = "grid/sandbox1/session1/artifact1"
        result = parse(key)
        
        expected = {
            "sandbox_id": "sandbox1",
            "session_id": "session1",
            "artifact_id": "artifact1",
            "subpath": None
        }
        assert result == expected
    
    def test_parse_valid_with_subpath(self):
        """Test parsing valid key with subpath."""
        key = "grid/sandbox1/session1/artifact1/sub/path"
        result = parse(key)
        
        expected = {
            "sandbox_id": "sandbox1",
            "session_id": "session1",
            "artifact_id": "artifact1",
            "subpath": "sub/path"
        }
        assert result == expected
    
    def test_parse_valid_complex_subpath(self):
        """Test parsing with complex subpath."""
        key = "grid/sandbox1/session1/artifact1/deep/nested/path"
        result = parse(key)
        
        expected = {
            "sandbox_id": "sandbox1",
            "session_id": "session1",
            "artifact_id": "artifact1",
            "subpath": "deep/nested/path"
        }
        assert result == expected
    
    def test_parse_invalid_empty_components(self):
        """Test parsing with empty components (now invalid)."""
        invalid_keys = [
            "grid//session1/artifact1",     # Empty sandbox
            "grid/sandbox1//artifact1",     # Empty session
            "grid/sandbox1/session1/",      # Empty artifact
            "grid///artifact1",             # Multiple empty
            "grid///",                      # All empty
        ]
        
        for key in invalid_keys:
            result = parse(key)
            assert result is None
    
    def test_parse_invalid_wrong_root(self):
        """Test parsing with wrong root."""
        invalid_keys = [
            "notgrid/sandbox1/session1/artifact1",
            "Grid/sandbox1/session1/artifact1",
            "GRID/sandbox1/session1/artifact1",
        ]
        
        for key in invalid_keys:
            result = parse(key)
            assert result is None
    
    def test_parse_invalid_too_few_parts(self):
        """Test parsing with too few parts."""
        invalid_keys = [
            "grid",
            "grid/sandbox1",
            "grid/sandbox1/session1",
        ]
        
        for key in invalid_keys:
            result = parse(key)
            assert result is None
    
    def test_parse_invalid_non_string(self):
        """Test parsing with non-string input."""
        invalid_inputs = [None, 123, [], {}]
        
        for invalid_input in invalid_inputs:
            result = parse(invalid_input)
            assert result is None
    
    def test_parse_empty_string(self):
        """Test parsing empty string."""
        result = parse("")
        assert result is None
    
    def test_parse_with_empty_subpath_component(self):
        """Test parsing with empty subpath component."""
        key = "grid/sandbox1/session1/artifact1/"
        result = parse(key)
        
        # Should still parse successfully, subpath becomes None
        assert result is not None
        assert result["subpath"] is None


class TestHelperFunctions:
    """Test helper functions."""
    
    def test_is_valid_grid_key_valid(self):
        """Test is_valid_grid_key with valid keys."""
        valid_keys = [
            "grid/sandbox1/session1/artifact1",
            "grid/a/b/c",
            "grid/sandbox-1/session_2/artifact.3",
            "grid/sandbox1/session1/artifact1/sub/path",
        ]
        
        for key in valid_keys:
            assert is_valid_grid_key(key) is True
    
    def test_is_valid_grid_key_invalid(self):
        """Test is_valid_grid_key with invalid keys."""
        invalid_keys = [
            "grid//session1/artifact1",      # Empty sandbox
            "grid/sandbox1//artifact1",      # Empty session
            "grid/sandbox1/session1/",       # Empty artifact
            "notgrid/sandbox1/session1/artifact1",  # Wrong root
            "grid/sandbox1/session1",        # Too few parts
            "",                              # Empty string
        ]
        
        for key in invalid_keys:
            assert is_valid_grid_key(key) is False
    
    def test_validate_grid_key_valid(self):
        """Test validate_grid_key with valid key."""
        key = "grid/sandbox1/session1/artifact1"
        result = validate_grid_key(key)
        
        expected = {
            "sandbox_id": "sandbox1",
            "session_id": "session1", 
            "artifact_id": "artifact1",
            "subpath": None
        }
        assert result == expected
    
    def test_validate_grid_key_invalid(self):
        """Test validate_grid_key with invalid key."""
        invalid_key = "grid//session1/artifact1"
        
        with pytest.raises(GridError) as exc_info:
            validate_grid_key(invalid_key)
        
        assert "Invalid grid key" in str(exc_info.value)
        assert invalid_key in str(exc_info.value)


class TestRoundTripOperations:
    """Test round-trip operations work with validation."""
    
    def test_generate_and_parse_roundtrip(self):
        """Test generating and parsing keys works correctly."""
        test_cases = [
            ("sandbox1", "session1", "artifact1"),
            ("prod-env", "user-123", "file-456"),
            ("a", "b", "c"),
            ("sandbox_test", "session-test", "artifact.test"),
        ]
        
        for sandbox_id, session_id, artifact_id in test_cases:
            # Generate key
            key = artifact_key(sandbox_id, session_id, artifact_id)
            
            # Parse it back
            parsed = parse(key)
            
            # Verify round-trip
            assert parsed is not None
            assert parsed["sandbox_id"] == sandbox_id
            assert parsed["session_id"] == session_id
            assert parsed["artifact_id"] == artifact_id
            assert parsed["subpath"] is None
    
    def test_prefix_and_key_compatibility(self):
        """Test that prefixes and keys are compatible."""
        sandbox_id = "test-sandbox"
        session_id = "test-session"
        artifact_id = "test-artifact"
        
        # Generate prefix and key
        prefix = canonical_prefix(sandbox_id, session_id)
        key = artifact_key(sandbox_id, session_id, artifact_id)
        
        # Key should start with prefix (minus trailing slash)
        assert key.startswith(prefix.rstrip("/"))
        
        # Parse and regenerate should match
        parsed = parse(key)
        regenerated_prefix = canonical_prefix(parsed["sandbox_id"], parsed["session_id"])
        assert regenerated_prefix == prefix


class TestValidationBehaviorDifferences:
    """Test differences between strict and lenient validation."""
    
    def test_empty_component_handling(self):
        """Test how empty components are handled in validation."""
        # These should fail validation in generation
        with pytest.raises(GridError):
            canonical_prefix("", "session1")
        
        with pytest.raises(GridError):
            artifact_key("sandbox1", "", "artifact1")
        
        # Empty components should also fail in parsing
        invalid_keys_with_empty_components = [
            "grid//session1/artifact1",      # Empty sandbox
            "grid/sandbox1//artifact1",      # Empty session  
            "grid/sandbox1/session1/",       # Empty artifact
            "grid///artifact1",              # Multiple empty components
        ]
        
        for key in invalid_keys_with_empty_components:
            result = parse(key)
            assert result is None
    
    def test_slash_injection_prevention(self):
        """Test that slash injection is prevented."""
        # These should all fail in generation
        with pytest.raises(GridError):
            canonical_prefix("sandbox/injection", "session1")
        
        with pytest.raises(GridError):
            artifact_key("sandbox1", "session/injection", "artifact1")
        
        with pytest.raises(GridError):
            artifact_key("sandbox1", "session1", "artifact/injection")
    
    def test_type_safety(self):
        """Test that type safety is enforced."""
        # Non-string inputs should fail
        with pytest.raises(GridError):
            canonical_prefix(123, "session1")
        
        with pytest.raises(GridError):
            artifact_key("sandbox1", None, "artifact1")
        
        # But parsing handles gracefully
        assert parse(123) is None
        assert parse(None) is None


class TestConstants:
    """Test module constants."""
    
    def test_root_constant(self):
        """Test that _ROOT constant is correct."""
        assert _ROOT == "grid"
        assert isinstance(_ROOT, str)
    
    def test_root_usage_consistency(self):
        """Test that _ROOT is used consistently."""
        prefix = canonical_prefix("test", "test")
        key = artifact_key("test", "test", "test")
        
        assert prefix.startswith(_ROOT + "/")
        assert key.startswith(_ROOT + "/")


class TestDocumentationExamples:
    """Test examples work as documented."""
    
    def test_basic_usage_examples(self):
        """Test basic usage examples."""
        # Generate canonical prefix
        prefix = canonical_prefix("production", "user-session-123")
        assert prefix == "grid/production/user-session-123/"
        
        # Generate artifact key
        key = artifact_key("production", "user-session-123", "document-456")
        assert key == "grid/production/user-session-123/document-456"
        
        # Parse the key
        parsed = parse(key)
        assert parsed["sandbox_id"] == "production"
        assert parsed["session_id"] == "user-session-123"
        assert parsed["artifact_id"] == "document-456"
        assert parsed["subpath"] is None
    
    def test_subpath_examples(self):
        """Test subpath handling examples."""
        # Key with subpath
        key_with_subpath = "grid/sandbox/session/artifact/folder/file.txt"
        parsed = parse(key_with_subpath)
        
        assert parsed["sandbox_id"] == "sandbox"
        assert parsed["session_id"] == "session"
        assert parsed["artifact_id"] == "artifact"
        assert parsed["subpath"] == "folder/file.txt"
    
    def test_validation_examples(self):
        """Test validation examples."""
        # Valid key
        assert is_valid_grid_key("grid/sandbox/session/artifact")
        
        # Invalid key
        assert not is_valid_grid_key("grid//session/artifact")
        
        # Validate with exception
        with pytest.raises(GridError):
            validate_grid_key("invalid/key")