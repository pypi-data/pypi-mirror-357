# chuk_mcp_runtime/tools/artifacts_tools.py
"""
Configurable MCP Tools Integration for chuk_artifacts

This module provides configurable MCP tools that can be enabled/disabled
and customized via config.yaml settings.
"""
import os
import json
import base64
from typing import List, Dict, Any, Optional, Union, Set
from datetime import datetime

# runtime
from chuk_artifacts import ArtifactStore, ArtifactNotFoundError
from chuk_mcp_runtime.common.mcp_tool_decorator import mcp_tool, TOOLS_REGISTRY
from chuk_mcp_runtime.session.session_management import validate_session_parameter
from chuk_mcp_runtime.server.logging_config import get_logger

# logger
logger = get_logger("chuk_mcp_runtime.tools.artifacts")

# Global artifact store instance and configuration
_artifact_store: Optional[ArtifactStore] = None
_artifacts_config: Dict[str, Any] = {}
_enabled_tools: Set[str] = set()

# Default tool configuration
DEFAULT_TOOL_CONFIG = {
    "enabled": False,  # Disabled by default - must be explicitly enabled in config
    "tools": {
        "upload_file": {"enabled": False, "description": "Upload files with base64 content"},
        "write_file": {"enabled": False, "description": "Create or update text files"},
        "read_file": {"enabled": False, "description": "Read file contents"},
        "list_session_files": {"enabled": False, "description": "List files in session"},
        "delete_file": {"enabled": False, "description": "Delete files"},
        "list_directory": {"enabled": False, "description": "List directory contents"},
        "copy_file": {"enabled": False, "description": "Copy files within session"},
        "move_file": {"enabled": False, "description": "Move/rename files"},
        "get_file_metadata": {"enabled": False, "description": "Get file metadata"},
        "get_presigned_url": {"enabled": False, "description": "Generate presigned URLs"},
        "get_storage_stats": {"enabled": False, "description": "Get storage statistics"},
    }
}


def configure_artifacts_tools(config: Dict[str, Any]) -> None:
    """Configure artifacts tools based on config.yaml settings."""
    global _artifacts_config, _enabled_tools
    
    # Get artifacts configuration
    _artifacts_config = config.get("artifacts", {})
    tools_config = _artifacts_config.get("tools", DEFAULT_TOOL_CONFIG)
    
    # Determine which tools are enabled
    _enabled_tools.clear()
    
    # check if tools are enabled
    if not tools_config.get("enabled", True):
        logger.info("Artifact tools disabled in configuration")
        return
    
    # Process individual tool configuration
    tool_settings = tools_config.get("tools", DEFAULT_TOOL_CONFIG["tools"])
    
    # loop through each tool and see if we should enable it
    for tool_name, tool_config in tool_settings.items():
        if tool_config.get("enabled", True):
            _enabled_tools.add(tool_name)
            logger.debug(f"Enabled artifact tool: {tool_name}")
        else:
            logger.debug(f"Disabled artifact tool: {tool_name}")
    
    # log it
    logger.info(f"Configured {len(_enabled_tools)} artifact tools: {', '.join(sorted(_enabled_tools))}")


def is_tool_enabled(tool_name: str) -> bool:
    """Check if a specific tool is enabled."""
    return tool_name in _enabled_tools


async def get_artifact_store() -> ArtifactStore:
    """Get or create the global artifact store instance."""
    global _artifact_store
    
    if _artifact_store is None:
        # Use configuration or environment variables or sensible defaults
        storage_provider = (
            _artifacts_config.get("storage_provider") or
            os.getenv("ARTIFACT_STORAGE_PROVIDER", "filesystem")
        )
        session_provider = (
            _artifacts_config.get("session_provider") or
            os.getenv("ARTIFACT_SESSION_PROVIDER", "memory")
        )
        bucket = (
            _artifacts_config.get("bucket") or
            os.getenv("ARTIFACT_BUCKET", "mcp-runtime")
        )
        
        # Set up filesystem root if using filesystem storage
        if storage_provider == "filesystem":
            fs_root = (
                _artifacts_config.get("filesystem_root") or
                os.getenv("ARTIFACT_FS_ROOT") or
                os.path.expanduser("~/.chuk_mcp_artifacts")
            )
            os.environ["ARTIFACT_FS_ROOT"] = fs_root
        
        _artifact_store = ArtifactStore(
            storage_provider=storage_provider,
            session_provider=session_provider,
            bucket=bucket
        )
        
        logger.info(f"Created artifact store: {storage_provider}/{session_provider} -> {bucket}")
    
    return _artifact_store


def _check_availability():
    """Check if chuk_artifacts is available and raise helpful error if not."""
    return True


def _check_tool_enabled(tool_name: str):
    """Check if a tool is enabled and raise error if not."""
    if not is_tool_enabled(tool_name):
        raise ValueError(f"Tool '{tool_name}' is disabled in configuration")


# ============================================================================
# Artifact Management Tools - All decorated with @mcp_tool
# ============================================================================

@mcp_tool(name="upload_file", description="Upload files with base64 content")
async def upload_file(
    content: str,
    filename: str,
    mime: str = "application/octet-stream",
    summary: str = "File uploaded via MCP",
    session_id: Optional[str] = None,
    meta: Optional[Dict[str, Any]] = None
) -> str:
    """
    Upload a file with base64 encoded content to the artifact store.
    
    Args:
        content: Base64 encoded file content
        filename: Name of the file to create
        mime: MIME type of the file (default: application/octet-stream)
        summary: Description of the file (default: File uploaded via MCP)
        session_id: Session ID (optional, will use current session if not provided)
        meta: Additional metadata for the file (optional)
        
    Returns:
        Success message with artifact ID
    """
    _check_tool_enabled("upload_file")
    effective_session = validate_session_parameter(session_id, "upload_file")
    store = await get_artifact_store()
    
    try:
        file_data = base64.b64decode(content)
        upload_meta = {
            "uploaded_via": "mcp",
            "upload_time": datetime.now().isoformat(),
            **(meta or {})
        }
        
        artifact_id = await store.store(
            data=file_data,
            mime=mime,
            summary=summary,
            filename=filename,
            session_id=effective_session,
            meta=upload_meta
        )
        
        return f"File uploaded successfully. Artifact ID: {artifact_id}"
        
    except Exception as e:
        raise ValueError(f"Failed to upload file: {str(e)}")


@mcp_tool(name="write_file", description="Create or update text files")
async def write_file(
    content: str,
    filename: str,
    mime: str = "text/plain",
    summary: str = "File created via MCP",
    session_id: Optional[str] = None,
    meta: Optional[Dict[str, Any]] = None
) -> str:
    """
    Create or update a text file in the artifact store.
    
    Args:
        content: Text content of the file
        filename: Name of the file to create
        mime: MIME type of the file (default: text/plain)
        summary: Description of the file (default: File created via MCP)
        session_id: Session ID (optional, will use current session if not provided)
        meta: Additional metadata for the file (optional)
        
    Returns:
        Success message with artifact ID
    """
    _check_tool_enabled("write_file")
    effective_session = validate_session_parameter(session_id, "write_file")
    store = await get_artifact_store()
    
    try:
        write_meta = {
            "created_via": "mcp",
            "creation_time": datetime.now().isoformat(),
            **(meta or {})
        }
        
        artifact_id = await store.write_file(
            content=content,
            filename=filename,
            mime=mime,
            summary=summary,
            session_id=effective_session,
            meta=write_meta
        )
        
        return f"File created successfully. Artifact ID: {artifact_id}"
        
    except Exception as e:
        raise ValueError(f"Failed to write file: {str(e)}")


@mcp_tool(name="read_file", description="Read file contents")
async def read_file(
    artifact_id: str,
    as_text: bool = True,
    session_id: Optional[str] = None
) -> Union[str, Dict[str, Any]]:
    """
    Read the content of a file from the artifact store.
    
    Args:
        artifact_id: Unique identifier of the file to read
        as_text: Whether to return content as text (default: True) or as binary with metadata
        session_id: Session ID (optional, will use current session if not provided)
        
    Returns:
        File content as text, or dictionary with content and metadata if as_text=False
    """
    _check_tool_enabled("read_file")
    effective_session = validate_session_parameter(session_id, "read_file")
    store = await get_artifact_store()
    
    try:
        if as_text:
            content = await store.read_file(artifact_id, as_text=True)
            return content
        else:
            data = await store.retrieve(artifact_id)
            metadata = await store.metadata(artifact_id)
            
            return {
                "content": base64.b64encode(data).decode(),
                "filename": metadata.get("filename", "unknown"),
                "mime": metadata.get("mime", "application/octet-stream"),
                "size": len(data),
                "metadata": metadata
            }
        
    except ArtifactNotFoundError:
        raise ValueError(f"File not found: {artifact_id}")
    except Exception as e:
        raise ValueError(f"Failed to read file: {str(e)}")


@mcp_tool(name="list_session_files", description="List files in session")
async def list_session_files(
    session_id: Optional[str] = None,
    include_metadata: bool = False
) -> List[Dict[str, Any]]:
    """
    List all files in the specified session.
    
    Args:
        session_id: Session ID (optional, will use current session if not provided)
        include_metadata: Whether to include full metadata for each file (default: False)
        
    Returns:
        List of files in the session with basic or full metadata
    """
    _check_tool_enabled("list_session_files")
    effective_session = validate_session_parameter(session_id, "list_session_files")
    store = await get_artifact_store()
    
    try:
        files = await store.list_by_session(effective_session)
        
        if include_metadata:
            return files
        else:
            return [
                {
                    "artifact_id": f.get("artifact_id"),
                    "filename": f.get("filename", "unknown"),
                    "mime": f.get("mime", "unknown"),
                    "bytes": f.get("bytes", 0),
                    "summary": f.get("summary", ""),
                    "created": f.get("created", "")
                }
                for f in files
            ]
        
    except Exception as e:
        raise ValueError(f"Failed to list files: {str(e)}")


@mcp_tool(name="delete_file", description="Delete files")
async def delete_file(
    artifact_id: str,
    session_id: Optional[str] = None
) -> str:
    """
    Delete a file from the artifact store.
    
    Args:
        artifact_id: Unique identifier of the file to delete
        session_id: Session ID (optional, will use current session if not provided)
        
    Returns:
        Success or failure message
    """
    _check_tool_enabled("delete_file")
    effective_session = validate_session_parameter(session_id, "delete_file")
    store = await get_artifact_store()
    
    try:
        deleted = await store.delete(artifact_id)
        
        if deleted:
            return f"File deleted successfully: {artifact_id}"
        else:
            return f"File not found or already deleted: {artifact_id}"
        
    except Exception as e:
        raise ValueError(f"Failed to delete file: {str(e)}")


@mcp_tool(name="list_directory", description="List directory contents")
async def list_directory(
    directory_path: str,
    session_id: Optional[str] = None
) -> List[Dict[str, Any]]:
    """
    List files in a specific directory within the session.
    
    Args:
        directory_path: Path to the directory to list
        session_id: Session ID (optional, will use current session if not provided)
        
    Returns:
        List of files in the specified directory
    """
    _check_tool_enabled("list_directory")
    effective_session = validate_session_parameter(session_id, "list_directory")
    store = await get_artifact_store()
    
    try:
        files = await store.get_directory_contents(effective_session, directory_path)
        
        return [
            {
                "artifact_id": f.get("artifact_id"),
                "filename": f.get("filename", "unknown"),
                "mime": f.get("mime", "unknown"),
                "bytes": f.get("bytes", 0),
                "summary": f.get("summary", "")
            }
            for f in files
        ]
        
    except Exception as e:
        raise ValueError(f"Failed to list directory: {str(e)}")


@mcp_tool(name="copy_file", description="Copy files within session")
async def copy_file(
    artifact_id: str,
    new_filename: str,
    new_summary: Optional[str] = None,
    session_id: Optional[str] = None,
    meta: Optional[Dict[str, Any]] = None
) -> str:
    """
    Copy a file within the same session.
    
    Args:
        artifact_id: Unique identifier of the file to copy
        new_filename: Name for the copied file
        new_summary: Description for the copied file (optional)
        session_id: Session ID (optional, will use current session if not provided)
        meta: Additional metadata for the copied file (optional)
        
    Returns:
        Success message with new artifact ID
    """
    _check_tool_enabled("copy_file")
    effective_session = validate_session_parameter(session_id, "copy_file")
    store = await get_artifact_store()
    
    try:
        copy_meta = {
            "copied_via": "mcp",
            "copy_time": datetime.now().isoformat(),
            "original_artifact_id": artifact_id,
            **(meta or {})
        }
        
        # Use the actual API parameters that work
        new_artifact_id = await store.copy_file(
            artifact_id,
            new_filename=new_filename,
            new_meta=copy_meta
        )
        
        return f"File copied successfully. New artifact ID: {new_artifact_id}"
        
    except Exception as e:
        raise ValueError(f"Failed to copy file: {str(e)}")


@mcp_tool(name="move_file", description="Move/rename files")
async def move_file(
    artifact_id: str,
    new_filename: str,
    new_summary: Optional[str] = None,
    session_id: Optional[str] = None,
    meta: Optional[Dict[str, Any]] = None
) -> str:
    """
    Move/rename a file within the same session.
    
    Args:
        artifact_id: Unique identifier of the file to move/rename
        new_filename: New name for the file
        new_summary: New description for the file (optional)
        session_id: Session ID (optional, will use current session if not provided)
        meta: Additional metadata for the moved file (optional)
        
    Returns:
        Success message confirming the move
    """
    _check_tool_enabled("move_file")
    effective_session = validate_session_parameter(session_id, "move_file")
    store = await get_artifact_store()
    
    try:
        move_meta = {
            "moved_via": "mcp",
            "move_time": datetime.now().isoformat(),
            **(meta or {})
        }
        
        await store.move_file(
            artifact_id,
            new_filename=new_filename,
            new_meta=move_meta
        )
        
        return f"File moved successfully: {artifact_id} -> {new_filename}"
        
    except Exception as e:
        raise ValueError(f"Failed to move file: {str(e)}")


@mcp_tool(name="get_file_metadata", description="Get file metadata")
async def get_file_metadata(
    artifact_id: str,
    session_id: Optional[str] = None
) -> Dict[str, Any]:
    """
    Get detailed metadata for a file.
    
    Args:
        artifact_id: Unique identifier of the file
        session_id: Session ID (optional, will use current session if not provided)
        
    Returns:
        Dictionary containing file metadata (size, type, creation date, etc.)
    """
    _check_tool_enabled("get_file_metadata")
    effective_session = validate_session_parameter(session_id, "get_file_metadata")
    store = await get_artifact_store()
    
    try:
        metadata = await store.metadata(artifact_id)
        return metadata
        
    except ArtifactNotFoundError:
        raise ValueError(f"File not found: {artifact_id}")
    except Exception as e:
        raise ValueError(f"Failed to get metadata: {str(e)}")


@mcp_tool(name="get_presigned_url", description="Generate presigned URLs")
async def get_presigned_url(
    artifact_id: str,
    expires_in: str = "medium",
    session_id: Optional[str] = None
) -> str:
    """
    Get a presigned URL for downloading a file.
    
    Args:
        artifact_id: Unique identifier of the file
        expires_in: URL expiration time - 'short', 'medium', or 'long' (default: medium)
        session_id: Session ID (optional, will use current session if not provided)
        
    Returns:
        Presigned URL for downloading the file
    """
    _check_tool_enabled("get_presigned_url")
    effective_session = validate_session_parameter(session_id, "get_presigned_url")
    store = await get_artifact_store()
    
    try:
        if expires_in == "short":
            url = await store.presign_short(artifact_id)
        elif expires_in == "long":
            url = await store.presign_long(artifact_id)
        else:  # medium (default)
            url = await store.presign_medium(artifact_id)
        
        return url
        
    except ArtifactNotFoundError:
        raise ValueError(f"File not found: {artifact_id}")
    except Exception as e:
        raise ValueError(f"Failed to generate presigned URL: {str(e)}")


@mcp_tool(name="get_storage_stats", description="Get storage statistics")
async def get_storage_stats(
    session_id: Optional[str] = None
) -> Dict[str, Any]:
    """
    Get statistics about the artifact store.
    
    Args:
        session_id: Session ID (optional, will use current session if not provided)
        
    Returns:
        Dictionary with storage statistics including file count and total bytes
    """
    _check_tool_enabled("get_storage_stats")
    effective_session = validate_session_parameter(session_id, "get_storage_stats")
    store = await get_artifact_store()
    
    try:
        stats = await store.get_stats()
        session_files = await store.list_by_session(effective_session)
        session_stats = {
            "session_id": effective_session,
            "session_file_count": len(session_files),
            "session_total_bytes": sum(f.get("bytes", 0) for f in session_files),
        }
        
        stats.update(session_stats)
        return stats
        
    except Exception as e:
        raise ValueError(f"Failed to get storage stats: {str(e)}")


# ============================================================================
# Registration and Utility Functions
# ============================================================================

# Map of tool name to function
TOOL_FUNCTIONS = {
    "upload_file": upload_file,
    "write_file": write_file,
    "read_file": read_file,
    "list_session_files": list_session_files,
    "delete_file": delete_file,
    "list_directory": list_directory,
    "copy_file": copy_file,
    "move_file": move_file,
    "get_file_metadata": get_file_metadata,
    "get_presigned_url": get_presigned_url,
    "get_storage_stats": get_storage_stats,
}

# ============================================================================
# Registration function for artifact-management helpers
# ============================================================================

async def register_artifacts_tools(config: Dict[str, Any] | None = None) -> bool:
    """Register artifact helpers according to *config*."""
    art_cfg = (config or {}).get("artifacts", {})
    if not art_cfg.get("enabled", False):
        for t in TOOL_FUNCTIONS:
            TOOLS_REGISTRY.pop(t, None)
        logger.info("artifacts block disabled - no helpers registered")
        return False

    enabled_helpers = {
        n for n, tc in art_cfg.get("tools", {}).items() if tc.get("enabled", False)
    }
    if not enabled_helpers:
        for t in TOOL_FUNCTIONS:
            TOOLS_REGISTRY.pop(t, None)
        logger.info("all artifact helpers disabled individually")
        return False

    # 1) make sure store is OK
    await get_artifact_store()          # raises if mis-configured

    # 2) prune everything that might still be there
    for t in TOOL_FUNCTIONS:
        TOOLS_REGISTRY.pop(t, None)

    # ---- KEEP _enabled_tools IN-SYNC ---------------------------------
    _enabled_tools.clear()
    _enabled_tools.update(enabled_helpers)
    # ------------------------------------------------------------------

    # 3) register the wanted helpers
    registered = 0
    for name in enabled_helpers:
        fn = TOOL_FUNCTIONS[name]
        if getattr(fn, "_needs_init", False):
            from chuk_mcp_runtime.common.mcp_tool_decorator import _initialize_tool
            await _initialize_tool(name, fn)
            fn = TOOLS_REGISTRY.get(name, fn)
        TOOLS_REGISTRY[name] = fn
        registered += 1
        logger.debug("Registered artifact helper: %s", name)

    logger.info(
        "Registered %d artifact helper(s): %s",
        registered, ", ".join(sorted(enabled_helpers)),
    )
    return bool(registered)


def get_artifacts_tools_info() -> Dict[str, Any]:
    """Get information about available and configured artifact tools."""
    all_tools = list(DEFAULT_TOOL_CONFIG["tools"].keys())
    
    return {
        "available": True,
        "configured": bool(_artifacts_config),
        "enabled_tools": list(_enabled_tools),
        "disabled_tools": [t for t in all_tools if t not in _enabled_tools],
        "total_tools": len(all_tools),
        "enabled_count": len(_enabled_tools),
        "config": _artifacts_config
    }


def get_enabled_tools() -> List[str]:
    """Get list of currently enabled tools."""
    return list(_enabled_tools)


# Tool list for external reference (all possible tools)
ALL_ARTIFACT_TOOLS = list(DEFAULT_TOOL_CONFIG["tools"].keys())

# Dynamic tool list based on configuration
def get_artifact_tools() -> List[str]:
    """Get currently enabled artifact tools."""
    return get_enabled_tools()


# Legacy property-style access (keeping for compatibility)
@property  
def ARTIFACT_TOOLS() -> List[str]:
    """Get currently enabled artifact tools."""
    return get_enabled_tools()