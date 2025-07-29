# Debug and Legacy Files

This directory contains debug scripts, development tools, and legacy test files that were used during the development process.

## 🚨 **Important Note**
These files are **NOT** for production use. They are kept for:
- Development reference
- Debugging specific issues
- Historical context of implementation decisions

## Files

### Authentication & Token Flow Debug
- `debug_auth_integration.py` - Debug authentication integration between HTTP headers and tool execution
- `debug_token_flow.py` - Debug Meta API token validation and flow
- `debug_meta_api_tool.py` - Debug Meta API tool functionality

### Server Configuration Debug  
- `debug_fastmcp_config.py` - Debug FastMCP server configuration and HTTP transport setup

### Legacy Test Files
- `test_streamable_http_old.py` - Original HTTP transport test (superseded by `tests/test_http_transport.py`)
- `test_meta_ads_auth.py` - Legacy authentication test
- `test_pipeboard_auth.py` - Legacy Pipeboard authentication test

## Usage Guidelines

**For Development:**
- These scripts may have hardcoded values, test tokens, or development-specific configurations
- They may not follow production coding standards
- Use them as reference only

**For Production:**
- Use the organized `tests/` directory for proper testing
- Use the `examples/` directory for integration examples
- Use the main package (`meta_ads_mcp/`) for actual functionality

## Cleanup Policy

Files in this directory may be removed in future releases once they're no longer needed for debugging or reference purposes. 