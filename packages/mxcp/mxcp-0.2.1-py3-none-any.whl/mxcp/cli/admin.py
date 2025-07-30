import click
from typing import Optional
from mxcp.cli.utils import output_error, configure_logging, get_env_profile
from mxcp.config.user_config import load_user_config
from mxcp.config.site_config import load_site_config
from mxcp.config.analytics import track_command_with_timing
import asyncio
import signal
import sys


@click.command(name="admin")
@click.option("--profile", help="Profile name to use")
@click.option("--readonly", is_flag=True, help="Start in read-only mode")
@click.option("--debug", is_flag=True, help="Show detailed debug information")
@track_command_with_timing("admin")
def admin(profile: Optional[str], readonly: bool, debug: bool):
    """Launch the mxcp terminal UI for administration and monitoring.
    
    This command starts an interactive terminal UI that provides:
    - Dashboard with system overview and activity monitoring
    - Endpoint management (view, test, validate)
    - SQL query interface with schema browser
    - Test runner with real-time results
    - Audit log viewer with filtering
    - Drift detection and comparison
    
    The UI adapts based on the mode:
    - Full mode (default): All features including modifications
    - Read-only mode: Monitoring and viewing only
    
    \b
    Examples:
        mxcp admin                    # Launch in full mode
        mxcp admin --readonly         # Launch in read-only mode
        mxcp admin --profile prod     # Use production profile
    
    \b
    Keyboard shortcuts:
        Ctrl+Q    - Quit
        F1        - Help
        F12       - Toggle read-only mode
        Tab       - Navigate between panels
        Ctrl+R    - Refresh data
    """
    # Get profile from environment if not specified
    if not profile:
        profile = get_env_profile()
        
    # Configure logging
    configure_logging(debug)
    
    try:
        # Lazy import to avoid loading TUI dependencies unless needed
        from mxcp.tui.app import MxcpTUI
        
        # Load configurations
        site_config = load_site_config()
        if profile:
            site_config['profile'] = profile
            
        user_config = load_user_config(site_config)
        
        # Create and run the TUI app
        app = MxcpTUI(
            readonly=readonly,
            profile=profile or site_config.get('profile', 'default')
        )
        
        # Set up signal handlers for graceful shutdown
        def signal_handler(signum, frame):
            if hasattr(app, '_refresh_task') and app._refresh_task:
                app._refresh_task.cancel()
            sys.exit(0)
            
        signal.signal(signal.SIGINT, signal_handler)
        signal.signal(signal.SIGTERM, signal_handler)
        
        # Run the TUI
        app.run()
        
    except ImportError as e:
        if "textual" in str(e).lower():
            click.echo(click.style(
                "\n⚠️  Textual is not installed!\n\n"
                "The TUI requires the Textual framework. Install it with:\n\n"
                "  pip install textual\n",
                fg='yellow'
            ))
            sys.exit(1)
        else:
            raise
            
    except KeyboardInterrupt:
        # Clean exit on Ctrl+C
        pass
        
    except Exception as e:
        output_error(e, json_output=False, debug=debug) 