from llm_fragments_sourcehut import (
    srht_loader,
    srht_todo_loader,
    _parse_srht_todo_argument,
    _to_srht_markdown,
)
import pytest
from unittest.mock import patch, Mock


@pytest.mark.parametrize(
    "argument",
    ("~amolith/adresilo-server",),
)
def test_srht_loader(argument):
    fragments = srht_loader(argument)
    by_source = {
        fragment.source.replace("\\", "/").split("/", 1)[1]: str(fragment)
        for fragment in fragments
    }

    # Check for a few key files. Their content may change, so we check for presence and start.
    assert "adresilo-server/README.md" in by_source
    assert by_source["adresilo-server/README.md"].startswith("<!--")

    assert "adresilo-server/main.go" in by_source
    assert by_source["adresilo-server/main.go"].strip().startswith("//")

    # Test error cases
    with pytest.raises(ValueError) as ex:
        srht_loader("~amolith/nonexistent-repo")
    assert "Failed to clone repository" in str(ex.value)


class TestParseSrhtTodoArgument:
    """Test the _parse_srht_todo_argument function"""

    def test_full_url_format(self):
        """Test parsing full SourceHut todo URLs"""
        instance, owner, repo, number = _parse_srht_todo_argument(
            "https://todo.sr.ht/~amolith/test-repo/123"
        )
        assert instance == "https://todo.sr.ht"
        assert owner == "~amolith"
        assert repo == "test-repo"
        assert number == 123

    def test_custom_instance_with_scheme(self):
        """Test parsing custom instance with scheme"""
        instance, owner, repo, number = _parse_srht_todo_argument(
            "https://custom.sr.ht/~user/project/456"
        )
        assert instance == "https://custom.sr.ht"
        assert owner == "~user"
        assert repo == "project"
        assert number == 456

    def test_custom_instance_without_scheme(self):
        """Test parsing custom instance without scheme (defaults to https)"""
        instance, owner, repo, number = _parse_srht_todo_argument(
            "custom.sr.ht/~user/project/789"
        )
        assert instance == "https://custom.sr.ht"
        assert owner == "~user"
        assert repo == "project"
        assert number == 789

    def test_default_instance_format(self):
        """Test parsing default instance format (~owner/repo/number)"""
        instance, owner, repo, number = _parse_srht_todo_argument(
            "~amolith/test-repo/999"
        )
        assert instance == "https://todo.sr.ht"
        assert owner == "~amolith"
        assert repo == "test-repo"
        assert number == 999

    @pytest.mark.parametrize(
        "invalid_arg",
        [
            "invalid-format",
            "missing/tilde/123",
            "~owner/repo",  # Missing number
            "~owner/repo/abc",  # Non-numeric number
            "https://todo.sr.ht/~owner",  # Missing repo and number
            "~owner",  # Missing repo and number
            "",  # Empty string
        ],
    )
    def test_invalid_arguments(self, invalid_arg):
        """Test that invalid arguments raise ValueError"""
        with pytest.raises(ValueError) as ex:
            _parse_srht_todo_argument(invalid_arg)
        assert "Argument should be" in str(ex.value)


class TestToSrhtMarkdown:
    """Test the _to_srht_markdown function"""

    def test_todo_with_body_and_comments(self):
        """Test converting todo with body and comments to markdown"""
        todo = {
            "title": "Test Todo",
            "user": {"login": "test_user"},
            "body": "This is the todo body.",
        }
        comments = [
            {
                "user": {"login": "commenter1"},
                "body": "First comment",
            },
            {
                "user": {"login": "commenter2"},
                "body": "Second comment",
            },
        ]

        markdown = _to_srht_markdown(todo, comments)

        assert "# Test Todo\n" in markdown
        assert "*Posted by test_user*\n" in markdown
        assert "This is the todo body.\n" in markdown
        assert "### Comment by commenter1\n" in markdown
        assert "First comment\n" in markdown
        assert "### Comment by commenter2\n" in markdown
        assert "Second comment\n" in markdown
        assert (
            markdown.count("---\n") == 3
        )  # One after body, one after each comment

    def test_todo_without_body(self):
        """Test converting todo without body"""
        todo = {
            "title": "Test Todo Without Body",
            "user": {"login": "test_user"},
            "body": "",
        }
        comments = []

        markdown = _to_srht_markdown(todo, comments)

        assert "# Test Todo Without Body\n" in markdown
        assert "*Posted by test_user*\n" in markdown
        assert "---" not in markdown  # No separator when no body or comments

    def test_todo_without_comments(self):
        """Test converting todo without comments"""
        todo = {
            "title": "Test Todo No Comments",
            "user": {"login": "test_user"},
            "body": "Just a body, no comments.",
        }
        comments = []

        markdown = _to_srht_markdown(todo, comments)

        assert "# Test Todo No Comments\n" in markdown
        assert "*Posted by test_user*\n" in markdown
        assert "Just a body, no comments.\n" in markdown
        assert "### Comment by" not in markdown
        assert "---" not in markdown  # No separator when no comments

    def test_empty_comment_body(self):
        """Test handling comments with empty body"""
        todo = {
            "title": "Test Todo",
            "user": {"login": "test_user"},
            "body": "Main body",
        }
        comments = [
            {
                "user": {"login": "commenter1"},
                "body": None,  # Empty body
            },
        ]

        markdown = _to_srht_markdown(todo, comments)

        assert "### Comment by commenter1\n" in markdown
        assert markdown.endswith("---\n")


class TestSrhtTodoLoader:
    """Test the srht_todo_loader function with mocked API responses"""

    @patch("llm_fragments_sourcehut._srht_client")
    def test_successful_todo_load(self, mock_client):
        """Test successfully loading a todo with comments"""
        # Mock the API response
        mock_response = Mock()
        mock_response.json.return_value = {
            "data": {
                "user": {
                    "tracker": {
                        "ticket": {
                            "subject": "Test Todo Subject",
                            "body": "Test todo body content.",
                            "submitter": {"canonicalName": "~test_submitter"},
                            "events": {
                                "results": [
                                    {
                                        "changes": [
                                            {
                                                "__typename": "Comment",
                                                "author": {
                                                    "canonicalName": "~commenter1"
                                                },
                                                "text": "First comment text",
                                            }
                                        ]
                                    },
                                    {
                                        "changes": [
                                            {
                                                "__typename": "Comment",
                                                "author": {
                                                    "canonicalName": "~commenter2"
                                                },
                                                "text": "Second comment text",
                                            }
                                        ]
                                    },
                                ]
                            },
                        }
                    }
                }
            }
        }
        mock_client.return_value.post.return_value = mock_response

        fragment = srht_todo_loader("~test_user/test_tracker/123")

        assert "# Test Todo Subject" in str(fragment)
        assert "*Posted by ~test_submitter*" in str(fragment)
        assert "Test todo body content." in str(fragment)
        assert "### Comment by ~commenter1" in str(fragment)
        assert "First comment text" in str(fragment)
        assert "### Comment by ~commenter2" in str(fragment)
        assert "Second comment text" in str(fragment)
        assert (
            fragment.source == "https://todo.sr.ht/~test_user/test_tracker/123"
        )

    @patch("llm_fragments_sourcehut._srht_client")
    def test_todo_without_body_or_comments(self, mock_client):
        """Test loading a todo without body or comments"""
        mock_response = Mock()
        mock_response.json.return_value = {
            "data": {
                "user": {
                    "tracker": {
                        "ticket": {
                            "subject": "Minimal Todo",
                            "body": None,
                            "submitter": {"canonicalName": "~minimal_user"},
                            "events": {"results": []},
                        }
                    }
                }
            }
        }
        mock_client.return_value.post.return_value = mock_response

        fragment = srht_todo_loader("~test_user/test_tracker/456")

        assert "# Minimal Todo" in str(fragment)
        assert "*Posted by ~minimal_user*" in str(fragment)

    @patch("llm_fragments_sourcehut._srht_client")
    def test_api_error_response(self, mock_client):
        """Test handling API error responses"""
        mock_response = Mock()
        mock_response.json.return_value = {
            "errors": [{"message": "Tracker not found"}]
        }
        mock_client.return_value.post.return_value = mock_response

        with pytest.raises(ValueError) as ex:
            srht_todo_loader("~test_user/nonexistent/789")
        assert "SourceHut API error: Tracker not found" in str(ex.value)

    @patch("llm_fragments_sourcehut._srht_client")
    def test_todo_not_found(self, mock_client):
        """Test when todo is not found (null response)"""
        mock_response = Mock()
        mock_response.json.return_value = {
            "data": {"user": {"tracker": {"ticket": None}}}
        }
        mock_client.return_value.post.return_value = mock_response

        with pytest.raises(ValueError) as ex:
            srht_todo_loader("~test_user/test_tracker/999")
        assert "Todo #999 not found" in str(ex.value)

    @patch("llm_fragments_sourcehut._srht_client")
    def test_malformed_response(self, mock_client):
        """Test handling malformed API responses"""
        mock_response = Mock()
        mock_response.json.return_value = {"data": {"user": None}}
        mock_client.return_value.post.return_value = mock_response

        with pytest.raises(ValueError) as ex:
            srht_todo_loader("~test_user/test_tracker/111")
        assert "Todo or tracker not found" in str(ex.value)

    def test_invalid_argument_format(self):
        """Test invalid argument format raises appropriate error"""
        with pytest.raises(ValueError) as ex:
            srht_todo_loader("invalid-format")
        assert "Fragment must be todo:~owner/repo/NUMBER" in str(ex.value)

    @patch("llm_fragments_sourcehut._srht_client")
    def test_custom_instance_todo(self, mock_client):
        """Test loading todo from custom instance"""
        mock_response = Mock()
        mock_response.json.return_value = {
            "data": {
                "user": {
                    "tracker": {
                        "ticket": {
                            "subject": "Custom Instance Todo",
                            "body": "From custom instance",
                            "submitter": {"canonicalName": "~custom_user"},
                            "events": {"results": []},
                        }
                    }
                }
            }
        }
        mock_client.return_value.post.return_value = mock_response

        fragment = srht_todo_loader("custom.sr.ht/~test_user/test_tracker/222")

        # Verify the API was called with custom instance URL
        mock_client.return_value.post.assert_called_once()
        call_args = mock_client.return_value.post.call_args
        assert call_args[0][0] == "https://custom.sr.ht/query"
        assert (
            fragment.source
            == "https://custom.sr.ht/~test_user/test_tracker/222"
        )

    @patch("llm_fragments_sourcehut._srht_client")
    def test_http_error_handling(self, mock_client):
        """Test handling HTTP errors from API"""
        mock_response = Mock()
        mock_response.raise_for_status.side_effect = Exception("HTTP 500 Error")
        mock_client.return_value.post.return_value = mock_response

        with pytest.raises(Exception) as ex:
            srht_todo_loader("~test_user/test_tracker/333")
        assert "HTTP 500 Error" in str(ex.value)
