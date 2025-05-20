# Changelog

## [Unreleased]

## [0.11.1] - 2025-05-20

### Fixed
- **Jira & Confluence Read-Only Mode:** Resolved an `AttributeError` in Jira write tools and standardized read-only mode checks across all Jira and Confluence write-enabled tools. Introduced a `@check_write_access` decorator to correctly use the application context for these checks, ensuring consistent behavior. (Fixes #434, PR #438)

## [0.11.0] - 2025-05-18

### Added
- **Multi-User Authentication for HTTP Transports:** Implemented comprehensive multi-user authentication for `streamable-http` and `sse` transports. Users can now authenticate per-request using OAuth 2.0 Bearer tokens (Cloud) or Personal Access Tokens (PATs for Server/DC or Cloud API tokens). This enables operations under individual user permissions, enhancing security and context-awareness. (#416, #341)
- **Confluence `add_comment` Tool:** Introduced a new tool `confluence_add_comment` to allow programmatic addition of comments to Confluence pages. (#424, #276)
- **Enhanced Confluence Page Lookup:** The `confluence_get_page` tool now supports fetching pages by `title` and `space_key` in addition to `page_id`, providing more flexibility when page IDs are unknown. (#430)

### Fixed
- **Confluence User Profile Macros:** Correctly processes Confluence User Profile Macros (`<ac:structured-macro ac:name="profile">`), resolving an issue where macros were misinterpreted, leading to garbled output or raw macro tags. This includes better user detail fetching for Server/DC instances. (#419)

### Changed
- **Authentication Context Management:** Refactored server context and dependency injection to support dynamic, user-specific `JiraFetcher` and `ConfluenceFetcher` instances based on per-request authentication.
- **Dependencies:** Updated `fastmcp` and `mcp` to latest compatible versions. Added `cachetools` for potential future enhancements.

### Documentation
- Updated README with detailed instructions for setting up and using multi-user authentication with OAuth 2.0 and PATs, including IDE configuration examples.
- Added the new `confluence_add_comment` tool to the tool table in README.md. (#431)

## [0.10.6] - 2025-05-12

### Fixed
- Enhanced OAuth configuration detection to properly identify and prioritize OAuth 2.0 setup when all required variables are present, especially verifying ATLASSIAN_OAUTH_CLOUD_ID (#410)
- Improved OAuth 2.0 authentication method selection logic in environment configuration handling (#412)

### Documentation
- Restored and enhanced OAuth 2.0 (3LO) setup guide in README.md with clear step-by-step instructions (#411, #414)
- Added Docker-specific OAuth configuration examples, including token persistence via volume mounting (#413)
- Reorganized authentication methods in .env.example for improved clarity and user understanding (#414)
- Added expanded IDE integration examples for OAuth 2.0 configuration (#415)

## [0.10.5] - 2025-05-10

### Fixed
- Enhanced compatibility with various MCP clients by improving optional parameter handling in Jira and Confluence tools (#389, #407)
- Fixed type errors with FastMCP v2.3.1 by updating Context type hints (#408)

### Changed
- Updated dependencies to use FastMCP 2.3.x series

## [0.10.4] - 2025-05-10

### Added
- New `jira_get_user_profile` tool to fetch user information using various identifiers (#396)
- Added `offline_access` scope to OAuth configs to enable refresh tokens and prevent authentication failures (#381)

### Fixed
- Made optional string parameters in Confluence tools handle `None` values properly for better client compatibility (#389)
- Fixed OAuth callback errors and improved logging for easier troubleshooting (#402)

### Documentation
- Temporarily removed OAuth setup instructions pending validation in Docker environments (#404)
- Clarified Jira tool parameter descriptions, especially for the `assignee` field (#391, #395)
- Added security guidance for client secret handling in OAuth setup (#381)

## [0.10.3] - 2025-05-06

### Added
- **Proxy Support:** Added support for HTTP/S and SOCKS proxies. Configure globally using `HTTP_PROXY`, `HTTPS_PROXY`, `SOCKS_PROXY`, `NO_PROXY` environment variables, or use service-specific overrides like `JIRA_HTTPS_PROXY`, `CONFLUENCE_NO_PROXY`. (#260, #361)

### Fixed
- Fixed `Context is not available outside of a request` error occurring when running via `uvx` due to incompatibility with `fastmcp>=2.2.8`. Pinned `fastmcp` dependency to `<2.2.8` to ensure compatibility with the latest `mcp-atlassian` release when installed via `uvx`. (#383)

## [0.10.2] - 2025-05-06

### Fixed
- SSE server now binds to "0.0.0.0" for broader network access.

## [0.10.1] - 2025-05-05

### Fixed
- Re-added the `/healthz` endpoint for Kubernetes health probes, which was accidentally removed during the FastMCP v2 migration (#371). This restores the fix for #359.

## [0.10.0] - 2025-05-05

### Added
-   **OAuth 2.0 Authentication:** Added support for OAuth 2.0 (3LO) for Jira and Confluence Cloud, including an interactive `--oauth-setup` wizard for easier configuration. Uses `keyring` for secure token storage. (Fixes #238)
-   **Health Check Endpoint:** Introduced a `/healthz` endpoint for Kubernetes readiness/liveness probes when using the SSE transport mode. (Fixes #359)

### Changed
-   **Server Framework:** Migrated the core server implementation from the legacy `mcp` library to the modern `fastmcp>=2.2.5` framework. This includes a new server structure under `src/mcp_atlassian/servers/` and centralized context management. (Fixes #371)
-   **Jira Cloud Search Limit:** Updated Jira Cloud search to use `enhanced_jql_get_list_of_tickets`, allowing retrieval of more than the previous 50-issue limit per request. (Fixes #369)
-   **Docker:** Optimized Docker image build process for smaller size (using Alpine base images) and improved security (running as non-root user).

### Fixed
-   **Jira Cloud Search Count:** Corrected the `total` count reported in `jira_search` results for Jira Cloud instances, which was previously limited by the pagination size. (Refs #333)

### Removed
-   **Tools:** Removed the `jira_get_epic_issues` and `confluence_get_page_ancestors` tools. Their functionality can be achieved using the respective `search` tools with appropriate JQL/CQL queries. (Fixes #372)

### Internal
-   **Configuration:** Consolidated `ruff` and `mypy` configurations into `pyproject.toml`, removing legacy config files.

### Documentation
-   Simplified setup and usage instructions in the README, adding guidance for the new OAuth setup command (`uvx mcp-atlassian --oauth-setup`).

## [0.9.0] - 2025-05-01

### Added
- Added tool filtering capability via `--enabled-tools` flag and `ENABLED_TOOLS` environment variable (#354)
- Added Confluence page labels support with new tools: `confluence_get_labels` and `confluence_add_label` (#328)
- Added `jira_batch_get_changelogs` tool and pagination helper for efficiently fetching issue changelog data (#346)

### Changed
- Improved on-premise Confluence URL handling based on whether the instance is Cloud or Server/Data Center (#350)
- Refactored Jira code to improve quality and reduce technical debt, including better type safety and code organization (#345)
- Adopted centralized field formatting with new `_format_field_value_for_write` mechanism for Jira issue field handling (#357)

### Fixed
- Fixed labels not being correctly applied during Jira issue creation with improved field handling (#357)
- Fixed Jira Cloud searches by using `enhanced_jql` for Cloud and fixing startAt TypeErrors in pagination (#356)

## [0.8.4] - 2025-04-26

### Added
- Added `jira_create_sprint` tool for programmatically creating Jira sprints
- Added `get_issue_link_types()` method to retrieve all available issue link types
- Added corresponding MCP tool interfaces for link operations

### Changed
- Refactored `create_issue_link(data)` method to create links between issues
- Refactored `remove_issue_link(link_id)` method to remove existing links
- Updated project dependencies with `python-dateutil` and `types-python-dateutil`

### Fixed
- Fixed SSL verification environment variables being overwritten in Docker (#340)
- Corrected jira_update_issue example for assignee format (#339)

## [0.8.3] - 2025-04-24

### Removed
- Removed Resources functionality to resolve excessive startup API requests (#303)

## [0.8.2] - 2025-04-23

### Fixed
- Reverted the FastMCP v2 migration (commits `b434c1d`, `db5e7de`) to resolve critical errors introduced in v0.8.1, including issues with `jira_create_issue`, `get_issue`, `get_board_issues`, and `get_sprints_from_board`. This restores stability while the refactoring issues are investigated further. (Fixes #314, #315, #316, #318, #319)

## [0.8.1] - 2025-04-23

### Fixed
- Fixed Jira search pagination parameter mismatch by correctly passing 'start' instead of 'start_at' parameter
- Fixed Jira search result handling by updating issue extraction logic

## [0.8.0] - 2025-04-22

### Added
- Added `jira_update_sprint`
- Added `jira_search_fields` tool for fuzzy searching Jira fields

### Changed
- Migrated server architecture to FastMCP v2
- Enabled setting transport mode (stdio/sse) via TRANSPORT env var
- Added support for setting port number via PORT env var when using SSE transport
- Implemented proper precedence: CLI arguments > environment variables > defaults
- Enhanced startup with detailed connection feedback and sensitive data masking
- Added optional parent_id parameter for Confluence page updates

### Fixed
- Fixed Jira Server/Data Center assignee field handling by prioritizing user name over key
- Fixed issue with `jira_get_issue` and comments handling
- Fixed duplicate functions and improved typing in Jira mixins

### Other
- Added Docker installation as primary method in README
- Added version-specific tags for container images on ghcr.io
- Added .dockerignore and updated Dockerfile for improved build process

## [0.7.1] - 2025-04-18

### Fixed
- Fixed batch issue creation payload structure in `batch_create_issues` to correctly pass list directly to Jira API without double-wrapping in `issueUpdates` (#273).
- Fixed `jira_get_issue` tool to include comments when comment_limit>0 by correcting field name check from "comments" to "comment" in JiraIssue.to_simplified_dict() (#281, #275).
- Fixed AttributeError in `jira_get_epic_issues` tool when processing results (#280, #277).

## [0.7.0] - 2025-04-17

### Removed (Breaking Change)
- Removed `confluence_attach_content` tool due to usability and technical limitations, particularly with image uploads (#255, #242)

### Added
- Added Jira issue linking capabilities:
    - New tool `jira_create_issue_link` to create links between issues.
    - New tool `jira_remove_issue_link` to remove existing issue links.
    - Implemented underlying `LinksMixin` for link operations (#266).
- Added `jira_batch_create_issues` tool for creating multiple Jira issues efficiently via Jira's bulk API (#244).
    - Implemented underlying `batch_create_issues` method in `jira.IssuesMixin`.
- Added standard GitHub templates for Issues (Bug Report, Feature Request) and Pull Requests (#263, #265).

### Changed
- Enhanced `confluence_search` tool to use `siteSearch` by default for simple terms (improving relevance) with automatic fallback to `text` search for compatibility (#270).
- Added pagination support (via `startAt` parameter) to the `jira_get_epic_issues` tool (#271, #268).

### Docs
- Significantly improved README clarity, structure, examples, and configuration instructions (#256).
- Fixed minor typo in documentation (#258).

### Fixed
- (Internal fix related to pagination parameter handling in `get_epic_issues` logic, exposed via `jira_get_epic_issues` tool change) (#271, #268).
- Fixed type ignore comments to resolve CI mypy errors (#271).

## [0.6.5] - 2025-04-13

### Added
- Added content type inference for Confluence attachments (#252, #242)

### Changed
- Refactored Confluence models into modular directory structure (#251)
- Refactored Jira pydantic models into dedicated package for improved organization (#249)
- Added support for missing standard Jira fields in JiraIssue model (#250, #230)

### Fixed
- Fixed Jira Data Center/Server assignee lookup during issue creation (#248)
- Fixed handling of fixVersions in additional_fields (#247, #241)

## [0.6.4] - 2025-04-09

### Fixed
- Improved type restriction for `JiraIssue.requested_fields` and corrected `jira_search` argument description (#227, #226)
- Resolved Windsurf parsing error (#228)

## [0.6.3] - 2025-04-07

### Added
- Added support for Jira timetracking field with proper model field mapping (#217, #213)

### Changed
- Updated documentation to include fixVersions example in jira_create_issue additional_fields parameter (#216)

### Fixed
- Changed components parameter type from array to string for Windsurf compatibility (#215)

## [0.6.2] - 2025-04-05

### Added
- Enhanced component support for Jira issues to allow multiple components when creating tickets (#208, #115)

### Fixed
- Fixed variable scope issue in confluence_get_page_children where local variable 'pages' was not accessible due to improper indentation (#209, #206)

## [0.6.1] - 2025-04-05

### Added
- Return count metadata (`total`, `start_at`, `max_results`) in Jira search results (`jira_search`, `jira_get_project_issues`, `jira_get_epic_issues`) to enable pagination and count-based queries (#203, #164)

## [0.6.0] - 2025-04-05

### Added
- Add pagination support to Jira list tools with new `startAt` parameter for `jira_search`, `jira_get_project_issues`, and `jira_get_epic_issues` (#198)
- Add pytest workflow for automated testing across multiple Python versions (3.10, 3.11, 3.12) (#200)
- Add Smithery deployment and installation support (#194)

### Changed
- Unify pagination parameter names to 'startAt' across Jira tools for better consistency and developer experience (#201)
- Improve configuration documentation and readability in .env.example with clear sections and alternative options (#192)

### Fixed
- Fix model property access in JiraIssue to prevent custom fields from overriding model properties (#199)
- Fix read_resource signature to properly take in an AnyUrl and return str (#195)
- Correct command invocation instructions in README.md to use the `mcp-atlassian` script instead of incorrect `python -m` commands (#197)
- Update server tests for read_resource signature change (#199)

## [0.5.0] - 2025-04-03

### Added
- Add tools to retrieve Jira Agile boards (`jira_get_agile_boards`), sprints (`jira_get_sprints_from_board`), board issues (`jira_get_board_issues`), and sprint issues (`jira_get_sprint_issues`) (#166)
- Implement Jira attachment upload functionality via `jira_update_issue` tool using the `attachments` parameter (#168, #7ad3485)
- Add tool to attach content to Confluence pages (`confluence_attach_content`) (#178)
- Add explicit `MCPAtlassianAuthenticationError` for handling 401/403 authentication errors, providing clearer feedback for expired tokens or permission issues (#190, #183)

### Changed
- Improve custom field handling in `JiraIssue` model to automatically include all fields not explicitly processed under `custom_fields`, making more data accessible (#182)
- Enable basic authentication support (username/API token) for on-premise/Data Center Confluence instances, previously only token auth was explicitly checked (#173)
- General updates and refinements to Jira issue handling logic (#187)

### Fixed
- Parse `fixVersions` field correctly in Jira issues, previously missed (#162)
- Fix JQL error in `list_resources` when user identifier (e.g., email) contains special characters like '@' by properly quoting and escaping the identifier (#180, #172)
- Fix Confluence search (`confluence_search`) and resource reading (`read_resource` for space URIs) when using space keys that require quotes (e.g., personal spaces '~...', reserved CQL words, numeric keys) by adding conditional CQL identifier quoting (#185, #184)
- Fix Python C-level timestamp conversion error ("timestamp too large") when fetching user data from Jira Data Center 9.x instances by using a direct API request bypassing the problematic library parsing (#189, #171)

## [0.4.0] - 2025-03-28

### Added
- Added support for retrieving Jira custom fields via MCP API (#157)
- Added ability to download attachments from JIRA issues (#160)
- Added development environment with devcontainer support (#159)
- Added JiraBoards and get_all_agile_boards tool (#158)

## [0.3.1] - 2025-03-27

### Added
- Added support for Jira and Confluence search filtering (#133)

### Changed
- Refactored utils module into specialized sub-modules for better organization (#154)
- Updated documentation with new MCP setting guidance for Cursor IDE 0.47+ (#153)
- Reduced default logging level to WARNING for better client compatibility (#155)

### Fixed
- Fixed SSLError when using SSL verification bypass option (#150)
- Enabled legacy SSL renegotiation in Python 3.11+ environments

## [0.3.0] - 2025-03-25

### Added
- Added read-only mode to disable write operations
- Added CONTRIBUTING.md with development setup and workflow guidelines

### Enhanced
- Simplified README structure for better clarity
- Improved field parameter handling in jira_search function
- Enhanced documentation with focus on CLI arguments as primary configuration method

### Fixed
- Fixed fields parameter in jira_search function to properly filter returned fields

## [0.2.6] - 2025-03-22

### Added
- Added support for getting Confluence pages in raw format without converting to markdown

### Enhanced
- Enhanced Jira Epic creation with a two-step approach for better field handling
- Enhanced Epic field discovery with improved fallback mechanisms
- Enhanced test script to support test filtering and added new tests for Jira Epic creation

### Fixed
- Fixed SSL verification bypass for self-signed certificates
- Implemented proper SSL verification handling for Confluence and Jira servers

## [0.2.5] - 2025-03-18

### Added
- Added dynamic custom field retrieval in JiraIssue with pattern matching support

### Fixed
- Fixed to allow parent field for all issue types, not just subtasks
- Fixed user identification for Jira Data Center/Server instances with fallback mechanisms
- Fixed pre-commit errors and updated unit tests

## [0.2.4] - 2025-03-17

### Added
- Added support for Jira subtask creation with proper parent relationship handling
- Added method to prepare parent fields for subtasks
- Updated API documentation to include subtask creation guidance

## [0.2.3] - 2025-03-16

### Added
- Added user details retrieval by account ID in ConfluenceClient to support proper user mention handling
- Added Confluence page ancestors functionality for more reliable parent-child relationship tracking
- Added SSE transport support for improved performance and reliability

### Changed
- Refactored markdown conversion to ConfluencePreprocessor class
- Moved markdown_to_confluence_storage function from utils to ConfluencePreprocessor
- Updated documentation with SSE configuration guidance

## [0.2.2] - 2025-03-13

### Added
- Added Confluence get-children-page tool (#98)

### Changed
- Separated Jira and Confluence preprocessing logic for better maintainability (#99)
- Updated README.md with Composer and Agent mode screencaptures (#95, #101)
- Updated README.md with new demo GIF (#93)

### Fixed
- Fixed Confluence update page textcontent issue (#100)

## [0.2.1] - 2025-03-13

### Added
- Added Confluence Server/Data Center support with Personal Access Token authentication
- Added Confluence page delete tool

### Fixed
- Fixed error with confluence_delete_page function
- Fixed handling of 'fields' attribute error in Jira fetcher
- Removed duplicate content field in Confluence page metadata
- Improved Confluence search functionality
- Added Docker installation instructions

## [0.2.0] - 2025-03-12

### Changed
- Major refactoring of Atlassian integration components into modular mixin classes
- Added Pydantic models for type-safe API responses
- Enhanced unit tests with better mocks and fixtures
- Added support for testing with real API data

### Fixed
- Fixed Jira transition API type handling errors
- Improved handling of different status formats in update methods
- Added robust handling for missing fields in Jira search responses
- Enhanced field parsing and automatic field expansion

## [0.1.16] - 2025-03-09

### Fixed
- Fixed authentication for Jira Server/Data Center deployments
- Modified environment variable check to properly support Server/Data Center

## [0.1.15] - 2025-03-08

### Added
- Added Jira Server/Data Center support with Personal Access Token authentication
- Added new Jira worklog tools for time tracking and estimate management
- Added tools for Jira status transitions: `jira_get_transitions` and `jira_transition_issue`
- Added comprehensive Epic linking support with `jira_link_to_epic` and `jira_get_epic_issues` tools
- Implemented dynamic Jira field discovery for Epic-related fields
- Added SSL verification option for on-premise Jira installations
- Added support for bidirectional Markdown-Jira markup conversion

### Changed
- Enhanced Epic linking with support for different Jira configurations
- Improved JSON serialization and result formatting in Atlassian tool methods
- Simplified Markdown to Jira conversion using TextPreprocessor
- Standardized result formatting across different tool methods

### Fixed
- Fixed Jira status updates to respect workflow rules by using transitions
- Fixed Epic creation with dynamic field discovery across different Jira instances
- Fixed Jira comments and issue descriptions to properly convert Markdown syntax
- Improved error handling in transition_issue with detailed logging
- Enhanced numbered list handling for proper rendering in Jira
- Implemented direct HTTP approach for issue transitions for better compatibility

## [0.1.14] - 2025-03-05

### Fixed
- Changed `md2conf` dependency to `markdown-to-confluence`

## [0.1.13] - 2025-03-05

### Fixed
- Added missing `md2conf` dependency to fix ModuleNotFoundError

## [0.1.12] - 2025-03-04

### Added
- Added Confluence page creation and update capabilities with markdown-to-confluence support
- Enhanced resource and tool descriptions with more context and examples

## [0.1.11] - 2025-03-03

### Added
- Added support for setting and updating assignee in Jira issues
- Added Jira comment functionality and enhanced get_issue with comment support
- Enhanced resource filtering to focus on user-contributed content

## [0.1.10] - 2025-02-22

### Added
- Added CLI support with click for configurable server initialization
- Support environment variable loading from .env file
- Implement flexible configuration via command-line options

## [0.1.9] - 2025-02-21

### Added
- Added GitHub Actions workflow for linting
- Added comprehensive test coverage for Confluence and Jira services
- Added new Jira tools: create_issue, update_issue, delete_issue
- Added Cursor IDE configuration documentation

### Changed
- Enhanced Jira issue management methods with improved error handling
- Updated installation instructions with detailed configuration examples

### Fixed
- Fixed URL generation in Confluence methods by removing '/wiki' prefix
- Improved environment variable handling in configuration

## [0.1.8] - 2025-02-16

### Added
- Added Docker support with multi-stage build
- Added Smithery configuration for deployment

### Fixed
- Fixed Jira date parsing for various timezone formats
- Fixed document types import error
- Updated logging configuration

## [0.1.7] - 2024-12-20

### Changed
- Optimized Confluence search performance by removing individual page fetching
- Updated search results format to use pre-generated excerpts

## [0.1.6] - 2025-12-19

### Changed
- Lowered minimum Python version requirement from 3.13 to 3.10 for broader compatibility

## [0.1.5] - 2024-12-19

### Fixed
- Aligned comment metadata keys in Confluence comments endpoint
- Fixed handling of nested structure in Confluence spaces response
- Updated README.md with improved documentation

## [0.1.0] - 2024-12-04
