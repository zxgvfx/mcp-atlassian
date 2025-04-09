"""Tests for the Jira Search mixin."""

from unittest.mock import MagicMock

import pytest
import requests

from mcp_atlassian.jira.search import SearchMixin
from mcp_atlassian.models.jira import JiraIssue, JiraSearchResult


class TestSearchMixin:
    """Tests for the SearchMixin class."""

    @pytest.fixture
    def search_mixin(self, jira_client):
        """Create a SearchMixin instance with mocked dependencies."""
        mixin = SearchMixin(config=jira_client.config)
        mixin.jira = jira_client.jira

        # Mock methods that are typically provided by other mixins
        mixin._clean_text = MagicMock(side_effect=lambda text: text if text else "")

        return mixin

    def test_search_issues_basic(self, search_mixin):
        """Test basic search functionality."""
        # Setup mock response
        mock_issues = {
            "issues": [
                {
                    "id": "10001",
                    "key": "TEST-123",
                    "fields": {
                        "summary": "Test issue",
                        "issuetype": {"name": "Bug"},
                        "status": {"name": "Open"},
                        "description": "Issue description",
                        "created": "2024-01-01T10:00:00.000+0000",
                        "updated": "2024-01-01T11:00:00.000+0000",
                        "priority": {"name": "High"},
                    },
                }
            ],
            "total": 1,
            "startAt": 0,
            "maxResults": 50,
        }
        search_mixin.jira.jql.return_value = mock_issues
        search_mixin.config.url = "https://example.atlassian.net"

        # Call the method
        result = search_mixin.search_issues("project = TEST")

        # Verify
        search_mixin.jira.jql.assert_called_once_with(
            "project = TEST",
            fields="summary,description,status,assignee,reporter,labels,priority,created,updated,issuetype",
            start=0,
            limit=50,
            expand=None,
        )

        # Verify results
        assert isinstance(result, JiraSearchResult)
        assert len(result.issues) == 1
        assert all(isinstance(issue, JiraIssue) for issue in result.issues)
        assert result.total == 1
        assert result.start_at == 0
        assert result.max_results == 50

        # Check the first issue
        issue = result.issues[0]
        assert issue.key == "TEST-123"
        assert issue.summary == "Test issue"
        assert issue.description == "Issue description"
        assert issue.status is not None
        assert issue.status.name == "Open"
        assert issue.issue_type is not None
        assert issue.issue_type.name == "Bug"
        assert issue.priority is not None
        assert issue.priority.name == "High"

        # Remove backward compatibility checks
        assert "Issue description" in issue.description
        assert issue.key == "TEST-123"

    def test_search_issues_with_empty_description(self, search_mixin):
        """Test search with issues that have no description."""
        # Setup mock response
        mock_issues = {
            "issues": [
                {
                    "id": "10001",
                    "key": "TEST-123",
                    "fields": {
                        "summary": "Test issue",
                        "issuetype": {"name": "Bug"},
                        "status": {"name": "Open"},
                        "description": None,
                        "created": "2024-01-01T10:00:00.000+0000",
                        "updated": "2024-01-01T11:00:00.000+0000",
                    },
                }
            ],
            "total": 1,
            "startAt": 0,
            "maxResults": 50,
        }
        search_mixin.jira.jql.return_value = mock_issues

        # Call the method
        result = search_mixin.search_issues("project = TEST")

        # Verify results
        assert len(result.issues) == 1
        assert isinstance(result.issues[0], JiraIssue)
        assert result.issues[0].key == "TEST-123"
        assert result.issues[0].description is None
        assert result.issues[0].summary == "Test issue"

        # Update to use direct properties instead of backward compatibility
        assert "Test issue" in result.issues[0].summary

    def test_search_issues_with_missing_fields(self, search_mixin):
        """Test search with issues missing some fields."""
        # Setup mock response
        mock_issues = {
            "issues": [
                {
                    "key": "TEST-123",
                    "fields": {
                        "summary": "Test issue",
                        # Missing issuetype, status, etc.
                    },
                }
            ],
            "total": 1,
            "startAt": 0,
            "maxResults": 50,
        }
        search_mixin.jira.jql.return_value = mock_issues

        # Call the method
        result = search_mixin.search_issues("project = TEST")

        # Verify results
        assert len(result.issues) == 1
        assert isinstance(result.issues[0], JiraIssue)
        assert result.issues[0].key == "TEST-123"
        assert result.issues[0].summary == "Test issue"
        assert result.issues[0].status is None
        assert result.issues[0].issue_type is None

    def test_search_issues_with_empty_results(self, search_mixin):
        """Test search with no results."""
        # Setup mock response
        search_mixin.jira.jql.return_value = {"issues": []}

        # Call the method
        result = search_mixin.search_issues("project = NONEXISTENT")

        # Verify results
        assert isinstance(result, JiraSearchResult)
        assert len(result.issues) == 0
        assert result.total == 0

    def test_search_issues_with_error(self, search_mixin):
        """Test search with API error."""
        # Setup mock to raise exception
        search_mixin.jira.jql.side_effect = Exception("API Error")

        # Call the method and verify it raises the expected exception
        with pytest.raises(Exception, match="Error searching issues"):
            search_mixin.search_issues("project = TEST")

    def test_search_issues_with_projects_filter(self, search_mixin):
        """Test search with projects filter."""
        # Setup mock response
        mock_issues = {
            "issues": [
                {
                    "id": "10001",
                    "key": "TEST-123",
                    "fields": {
                        "summary": "Test issue",
                        "issuetype": {"name": "Bug"},
                        "status": {"name": "Open"},
                    },
                }
            ],
            "total": 1,
            "startAt": 0,
            "maxResults": 50,
        }
        search_mixin.jira.jql.return_value = mock_issues
        search_mixin.config.url = "https://example.atlassian.net"

        # Test with single project filter
        result = search_mixin.search_issues("text ~ 'test'", projects_filter="TEST")
        search_mixin.jira.jql.assert_called_with(
            "(text ~ 'test') AND project = TEST",
            fields="summary,description,status,assignee,reporter,labels,priority,created,updated,issuetype",
            start=0,
            limit=50,
            expand=None,
        )
        assert len(result.issues) == 1
        assert result.total == 1

        # Test with multiple project filter
        result = search_mixin.search_issues("text ~ 'test'", projects_filter="TEST,DEV")
        search_mixin.jira.jql.assert_called_with(
            '(text ~ \'test\') AND project IN ("TEST", "DEV")',
            fields="summary,description,status,assignee,reporter,labels,priority,created,updated,issuetype",
            start=0,
            limit=50,
            expand=None,
        )
        assert len(result.issues) == 1
        assert result.total == 1

    def test_search_issues_with_config_projects_filter(self, search_mixin):
        """Test search using projects filter from config."""
        # Setup mock response
        mock_issues = {
            "issues": [
                {
                    "id": "10001",
                    "key": "TEST-123",
                    "fields": {
                        "summary": "Test issue",
                        "issuetype": {"name": "Bug"},
                        "status": {"name": "Open"},
                    },
                }
            ],
            "total": 1,
            "startAt": 0,
            "maxResults": 50,
        }
        search_mixin.jira.jql.return_value = mock_issues
        search_mixin.config.url = "https://example.atlassian.net"
        search_mixin.config.projects_filter = "TEST,DEV"

        # Test with config filter
        result = search_mixin.search_issues("text ~ 'test'")
        search_mixin.jira.jql.assert_called_with(
            '(text ~ \'test\') AND project IN ("TEST", "DEV")',
            fields="summary,description,status,assignee,reporter,labels,priority,created,updated,issuetype",
            start=0,
            limit=50,
            expand=None,
        )
        assert len(result.issues) == 1
        assert result.total == 1

        # Test with override
        result = search_mixin.search_issues("text ~ 'test'", projects_filter="OVERRIDE")
        search_mixin.jira.jql.assert_called_with(
            "(text ~ 'test') AND project = OVERRIDE",
            fields="summary,description,status,assignee,reporter,labels,priority,created,updated,issuetype",
            start=0,
            limit=50,
            expand=None,
        )
        assert len(result.issues) == 1
        assert result.total == 1

        # Test with override - multiple projects
        result = search_mixin.search_issues(
            "text ~ 'test'", projects_filter="OVER1,OVER2"
        )
        search_mixin.jira.jql.assert_called_with(
            '(text ~ \'test\') AND project IN ("OVER1", "OVER2")',
            fields="summary,description,status,assignee,reporter,labels,priority,created,updated,issuetype",
            start=0,
            limit=50,
            expand=None,
        )
        assert len(result.issues) == 1
        assert result.total == 1

    def test_get_project_issues(self, search_mixin):
        """Test get_project_issues method."""
        # Setup mock response
        search_mixin.jira.jql.return_value = {"issues": []}

        # Call the method
        result = search_mixin.get_project_issues("TEST")

        # Verify JQL query
        search_mixin.jira.jql.assert_called_once_with(
            "project = TEST ORDER BY created DESC",
            fields="summary,description,status,assignee,reporter,labels,priority,created,updated,issuetype",
            start=0,
            limit=50,
            expand=None,
        )
        assert isinstance(result, JiraSearchResult)
        assert len(result.issues) == 0

    def test_get_epic_issues_success(self, search_mixin):
        """Test get_epic_issues method."""
        # Setup mock response
        search_mixin.jira.issue.return_value = {
            "key": "TEST-123",
            "fields": {"issuetype": {"name": "Epic"}},
        }
        search_mixin.jira.jql.return_value = {"issues": []}

        # Call the method
        result = search_mixin.get_epic_issues("TEST-123")

        # Verify JQL query
        search_mixin.jira.issue.assert_called_once_with("TEST-123")
        search_mixin.jira.jql.assert_called_once_with(
            'issueFunction in issuesScopedToEpic("TEST-123")',
            fields="summary,description,status,assignee,reporter,labels,priority,created,updated,issuetype",
            start=0,
            limit=50,
            expand=None,
        )
        assert isinstance(result, JiraSearchResult)
        assert len(result.issues) == 0

    def test_get_epic_issues_not_epic(self, search_mixin):
        """Test get_epic_issues with a non-epic issue."""
        # Setup mock response
        search_mixin.jira.issue.return_value = {
            "key": "TEST-123",
            "fields": {"issuetype": {"name": "Story"}},
        }

        # Call the method and verify it raises the expected exception
        with pytest.raises(ValueError, match="TEST-123 is not an Epic"):
            search_mixin.get_epic_issues("TEST-123")

    def test_get_epic_issues_with_field_ids(self, search_mixin):
        """Test get_epic_issues with custom Epic field IDs."""
        # Setup mock response with custom epic field ids
        epic_key = "TEST-123"
        search_mixin.config.epic_link_field = "customfield_10009"  # Example field ID
        search_mixin.config.epic_name_field = "customfield_10010"  # Example field ID

        # Mock responses using side effects
        def search_side_effect(jql, **kwargs):
            assert epic_key in jql
            return {
                "issues": [
                    {
                        "key": "TEST-124",
                        "fields": {
                            "summary": "Linked issue",
                            "customfield_10009": "TEST-123",  # Epic link
                        },
                    }
                ],
                "total": 1,
                "startAt": 0,
                "maxResults": 50,
            }

        search_mixin.jira.issue.return_value = {
            "key": epic_key,
            "fields": {
                "issuetype": {"name": "Epic"},
                "customfield_10010": "Epic Name",  # Epic name
            },
        }
        search_mixin.jira.jql.side_effect = search_side_effect

        # Call the method
        result = search_mixin.get_epic_issues(epic_key)

        # Verify
        assert isinstance(result, JiraSearchResult)
        assert len(result.issues) == 1
        assert result.issues[0].key == "TEST-124"
        assert result.issues[0].summary == "Linked issue"
        assert result.issues[0].custom_fields["customfield_10009"] == "TEST-123"

    def test_get_epic_issues_no_results(self, search_mixin):
        """Test get_epic_issues with no linked issues."""
        # Setup mock response
        search_mixin.jira.issue.return_value = {
            "key": "TEST-123",
            "fields": {"issuetype": {"name": "Epic"}},
        }
        search_mixin.jira.jql.return_value = {"issues": []}

        # Call the method
        result = search_mixin.get_epic_issues("TEST-123")

        # Verify results
        assert isinstance(result, JiraSearchResult)
        assert len(result.issues) == 0
        assert result.total == 0

    def test_get_epic_issues_with_error(self, search_mixin):
        """Test get_epic_issues with API error."""
        # Setup mock to raise exception on issue lookup
        search_mixin.jira.issue.side_effect = Exception("API Error")

        # Call the method and verify it raises the expected exception
        with pytest.raises(Exception, match="Error getting epic issues"):
            search_mixin.get_epic_issues("TEST-123")

    def test_parse_date(self, search_mixin):
        """Test the _parse_date method."""
        # Test with a valid date string
        result = search_mixin._parse_date("2024-01-01T10:00:00.000+0000")
        assert "2024-01-01" in result

        # Test with an empty string
        result = search_mixin._parse_date("")
        assert result == ""

    def test_search_issues_with_fields_parameter(self, search_mixin):
        """Test search with specific fields parameter, including custom fields."""
        # Setup mock response with a custom field
        mock_issues = {
            "issues": [
                {
                    "id": "10001",
                    "key": "TEST-123",
                    "fields": {
                        "summary": "Test issue with custom field",
                        "assignee": {
                            "displayName": "Test User",
                            "emailAddress": "test@example.com",
                            "active": True,
                        },
                        "customfield_10049": "Custom value",
                        "issuetype": {"name": "Bug"},
                        "status": {"name": "Open"},
                        "description": "Issue description",
                        "created": "2024-01-01T10:00:00.000+0000",
                        "updated": "2024-01-01T11:00:00.000+0000",
                        "priority": {"name": "High"},
                    },
                }
            ],
            "total": 1,
            "startAt": 0,
            "maxResults": 50,
        }
        search_mixin.jira.jql.return_value = mock_issues
        search_mixin.config.url = "https://example.atlassian.net"

        # Call the method with specific fields
        result = search_mixin.search_issues(
            "project = TEST", fields="summary,assignee,customfield_10049"
        )

        # Verify the JQL call includes the fields parameter
        search_mixin.jira.jql.assert_called_once_with(
            "project = TEST",
            fields="summary,assignee,customfield_10049",
            start=0,
            limit=50,
            expand=None,
        )

        # Verify results
        assert isinstance(result, JiraSearchResult)
        assert len(result.issues) == 1
        issue = result.issues[0]

        # Convert to simplified dict to check field filtering
        simplified = issue.to_simplified_dict()

        # These fields should be included (plus id and key which are always included)
        assert "id" in simplified
        assert "key" in simplified
        assert "summary" in simplified
        assert "assignee" in simplified
        assert "customfield_10049" in simplified

        # These fields should NOT be included
        assert "description" not in simplified
        assert "status" not in simplified
        assert "issue_type" not in simplified
        assert "priority" not in simplified
        assert "created" not in simplified
        assert "updated" not in simplified

        # Verify the values of included fields
        assert simplified["summary"] == "Test issue with custom field"
        assert simplified["assignee"]["name"] == "Test User"
        assert simplified["customfield_10049"] == "Custom value"

    def test_search_issues_with_start(self, search_mixin: SearchMixin) -> None:
        """Test searching issues with a start index."""
        search_mixin.jira.jql.return_value = {
            "issues": [
                {
                    "key": "PROJ-1",
                    "fields": {"summary": "Issue 1"},
                    "self": "https://test.atlassian.net/rest/api/2/issue/10001",
                }
            ],
            "total": 1,
            "startAt": 5,
            "maxResults": 10,
        }
        jql = "project = PROJ"
        start_index = 5

        result = search_mixin.search_issues(jql, start=start_index, limit=10)

        assert len(result.issues) == 1
        assert result.start_at == 5
        assert result.max_results == 10
        assert result.total == 1

        search_mixin.jira.jql.assert_called_once_with(
            jql,
            fields="summary,description,status,assignee,reporter,labels,priority,created,updated,issuetype",
            start=start_index,
            limit=10,
            expand=None,
        )

    def test_get_project_issues_with_start(self, search_mixin: SearchMixin) -> None:
        """Test getting project issues with a start index."""
        search_mixin.jira.jql.return_value = {
            "issues": [
                {
                    "key": "PROJ-2",
                    "fields": {"summary": "Issue 2"},
                    "self": "https://test.atlassian.net/rest/api/2/issue/10002",
                }
            ],
            "total": 1,
            "startAt": 3,
            "maxResults": 5,
        }
        project_key = "PROJ"
        start_index = 3

        result = search_mixin.get_project_issues(
            project_key, start=start_index, limit=5
        )

        assert len(result.issues) == 1
        assert result.start_at == 3
        assert result.max_results == 5
        assert result.total == 1

        expected_jql = f"project = {project_key} ORDER BY created DESC"
        search_mixin.jira.jql.assert_called_once_with(
            expected_jql,
            fields="summary,description,status,assignee,reporter,labels,priority,created,updated,issuetype",
            start=start_index,
            limit=5,
            expand=None,
        )

    def test_get_epic_issues_with_start(self, search_mixin: SearchMixin) -> None:
        """Test getting epic issues with a start index."""
        epic_key = "PROJ-100"
        # Mock the epic check first
        search_mixin.jira.issue.return_value = {
            "key": epic_key,
            "fields": {"issuetype": {"name": "Epic"}},
        }
        # Mock the JQL search
        search_mixin.jira.jql.return_value = {
            "issues": [
                {
                    "key": "PROJ-101",
                    "fields": {"summary": "Story 1"},
                    "self": "https://test.atlassian.net/rest/api/2/issue/10101",
                }
            ],
            "total": 1,
            "startAt": 2,
            "maxResults": 10,
        }
        start_index = 2

        result = search_mixin.get_epic_issues(epic_key, start=start_index, limit=10)

        assert len(result.issues) == 1
        assert result.start_at == 2
        assert result.max_results == 10
        assert result.total == 1

        # Check the epic issue call first
        search_mixin.jira.issue.assert_called_once_with(epic_key)
        # Check the JQL call (assuming issueFunction works)
        expected_jql = f'issueFunction in issuesScopedToEpic("{epic_key}")'
        search_mixin.jira.jql.assert_called_once_with(
            expected_jql,
            fields="summary,description,status,assignee,reporter,labels,priority,created,updated,issuetype",
            start=start_index,
            limit=10,
            expand=None,
        )

    def test_get_board_issues(self, search_mixin):
        """Test get_project_issues method."""
        mock_issues = {
            "issues": [
                {
                    "id": "10001",
                    "key": "TEST-123",
                    "fields": {
                        "summary": "Test issue",
                        "issuetype": {"name": "Bug"},
                        "status": {"name": "Open"},
                        "description": "Issue description",
                        "created": "2024-01-01T10:00:00.000+0000",
                        "updated": "2024-01-01T11:00:00.000+0000",
                        "priority": {"name": "High"},
                    },
                }
            ],
            "total": 1,
            "startAt": 0,
            "maxResults": 50,
        }
        search_mixin.jira.get_issues_for_board.return_value = mock_issues

        # Call the method
        result = search_mixin.get_board_issues("1000", jql="", limit=20)

        # Verify results
        assert isinstance(result, JiraSearchResult)
        assert len(result.issues) == 1
        assert all(isinstance(issue, JiraIssue) for issue in result.issues)
        assert result.total == 1
        assert result.start_at == 0
        assert result.max_results == 50

        # Check the first issue
        issue = result.issues[0]
        assert issue.key == "TEST-123"
        assert issue.summary == "Test issue"
        assert issue.description == "Issue description"
        assert issue.status is not None
        assert issue.status.name == "Open"
        assert issue.issue_type is not None
        assert issue.issue_type.name == "Bug"
        assert issue.priority is not None
        assert issue.priority.name == "High"

        # Remove backward compatibility checks
        assert "Issue description" in issue.description
        assert issue.key == "TEST-123"

    def test_get_board_issues_exception(self, search_mixin):
        search_mixin.jira.get_issues_for_board.side_effect = Exception("API Error")

        with pytest.raises(Exception) as e:
            search_mixin.get_board_issues("1000", jql="", limit=20)
        assert "API Error" in str(e.value)

    def test_get_board_issues_http_error(self, search_mixin):
        search_mixin.jira.get_issues_for_board.side_effect = requests.HTTPError(
            response=MagicMock(content="API Error content")
        )

        with pytest.raises(Exception) as e:
            search_mixin.get_board_issues("1000", jql="", limit=20)
        assert "API Error content" in str(e.value)

    def test_get_sprint_issues(self, search_mixin):
        """Test get_sprint_issues method."""
        mock_issues = {
            "issues": [
                {
                    "id": "10001",
                    "key": "TEST-123",
                    "fields": {
                        "summary": "Test issue",
                        "issuetype": {"name": "Bug"},
                        "status": {"name": "Open"},
                        "description": "Issue description",
                        "created": "2024-01-01T10:00:00.000+0000",
                        "updated": "2024-01-01T11:00:00.000+0000",
                        "priority": {"name": "High"},
                    },
                }
            ],
            "total": 1,
            "startAt": 0,
            "maxResults": 50,
        }
        search_mixin.jira.get_sprint_issues.return_value = mock_issues

        # Call the method
        result = search_mixin.get_sprint_issues("10001")

        # Verify results
        assert isinstance(result, JiraSearchResult)
        assert len(result.issues) == 1
        assert all(isinstance(issue, JiraIssue) for issue in result.issues)
        assert result.total == 1
        assert result.start_at == 0
        assert result.max_results == 50

        # Check the first issue
        issue = result.issues[0]
        assert issue.key == "TEST-123"
        assert issue.summary == "Test issue"
        assert issue.description == "Issue description"
        assert issue.status is not None
        assert issue.status.name == "Open"
        assert issue.issue_type is not None
        assert issue.issue_type.name == "Bug"
        assert issue.priority is not None
        assert issue.priority.name == "High"

    def test_get_sprint_issues_exception(self, search_mixin):
        search_mixin.jira.get_sprint_issues.side_effect = Exception("API Error")

        with pytest.raises(Exception) as e:
            search_mixin.get_sprint_issues("10001")
        assert "API Error" in str(e.value)

    def test_get_sprint_issues_http_error(self, search_mixin):
        search_mixin.jira.get_sprint_issues.side_effect = requests.HTTPError(
            response=MagicMock(content="API Error content")
        )

        with pytest.raises(Exception) as e:
            search_mixin.get_sprint_issues("10001")
        assert "API Error content" in str(e.value)
