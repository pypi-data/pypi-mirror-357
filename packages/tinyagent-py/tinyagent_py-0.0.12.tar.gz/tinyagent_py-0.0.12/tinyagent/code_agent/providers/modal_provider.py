import sys
import modal
import cloudpickle
from typing import Dict, List, Any, Optional, Union
from .base import CodeExecutionProvider
from ..utils import clean_response, make_session_blob, _run_python


class ModalProvider(CodeExecutionProvider):
    """
    Modal-based code execution provider.
    
    This provider uses Modal.com to execute Python code in a remote, sandboxed environment.
    It provides scalable, secure code execution with automatic dependency management.
    Can also run locally for development/testing purposes using Modal's native .local() method.
    """
    
    PYTHON_VERSION = f"{sys.version_info.major}.{sys.version_info.minor}"
    
    def __init__(
        self,
        log_manager,
        default_python_codes: Optional[List[str]] = None,
        code_tools: List[Dict[str, Any]] = None,
        pip_packages: List[str] | None = None,
        default_packages: Optional[List[str]] = None,
        apt_packages: Optional[List[str]] = None,
        python_version: Optional[str] = None,
        authorized_imports: list[str] | None = None,
        modal_secrets: Dict[str, Union[str, None]] | None = None,
        lazy_init: bool = True,
        sandbox_name: str = "tinycodeagent-sandbox",
        local_execution: bool = False,
        **kwargs
    ):
        """Create a ModalProvider instance.

        Additional keyword arguments (passed via **kwargs) are ignored by the
        base class but accepted here for forward-compatibility.

        Args:
            default_packages: Base set of Python packages installed into the
                sandbox image. If ``None`` a sane default list is used. The
                final set of installed packages is the union of
                ``default_packages`` and ``pip_packages``.
            apt_packages: Debian/Ubuntu APT packages to install into the image
                prior to ``pip install``. Defaults to an empty list.  Always
                installed *in addition to* the basics required by TinyAgent
                (git, curl, …) so you only need to specify the extras.
            python_version: Python version used for the sandbox image. If
                ``None`` the current interpreter version is used.
            authorized_imports: Optional allow-list of modules the user code is permitted to import. Supports wildcard patterns (e.g. "pandas.*"). If ``None`` the safety layer blocks only the predefined dangerous modules.
        """

        # Resolve default values ------------------------------------------------
        if default_packages is None:
            default_packages = [
                "cloudpickle",
                "requests",
                "tinyagent-py[all]",
                "gradio",
                "arize-phoenix-otel",
            ]

        if apt_packages is None:
            apt_packages = ["git", "curl", "nodejs", "npm"]

        if python_version is None:
            python_version = self.PYTHON_VERSION

        # Keep references so callers can introspect / mutate later -------------
        self.default_packages: List[str] = default_packages
        self.apt_packages: List[str] = apt_packages
        self.python_version: str = python_version
        self.authorized_imports = authorized_imports

        # ----------------------------------------------------------------------
        final_packages = list(set(self.default_packages + (pip_packages or [])))
        
        super().__init__(
            log_manager=log_manager,
            default_python_codes=default_python_codes or [],
            code_tools=code_tools or [],
            pip_packages=final_packages,
            secrets=modal_secrets or {},
            lazy_init=lazy_init,
            **kwargs
        )
        
        self.sandbox_name = sandbox_name
        self.local_execution = local_execution
        self.modal_secrets = modal.Secret.from_dict(self.secrets)
        self.app = None
        self._app_run_python = None
        self.is_trusted_code = kwargs.get("trust_code", False)
        
        self._setup_modal_app()
        
    def _setup_modal_app(self):
        """Set up the Modal application and functions."""
        execution_mode = "🏠 LOCAL" if self.local_execution else "☁️ REMOTE"
        print(f"{execution_mode} ModalProvider setting up Modal app")
        
        agent_image = modal.Image.debian_slim(python_version=self.python_version)

        # Install APT packages first (if any were requested)
        if self.apt_packages:
            agent_image = agent_image.apt_install(*self.apt_packages)

        # Then install pip packages (including the union of default + user)
        agent_image = agent_image.pip_install(*self.pip_packages)
        
        self.app = modal.App(
            name=self.sandbox_name,
            image=agent_image,
            secrets=[self.modal_secrets]
        )
        
        self._app_run_python = self.app.function()(_run_python)
        
        # Add tools if provided
        if self.code_tools:
            self.add_tools(self.code_tools)
    
    async def execute_python(self, code_lines: List[str], timeout: int = 120) -> Dict[str, Any]:
        """
        Execute Python code using Modal's native .local() or .remote() methods.
        
        Args:
            code_lines: List of Python code lines to execute
            timeout: Maximum execution time in seconds
            
        Returns:
            Dictionary containing execution results
        """
        if isinstance(code_lines, str):
            code_lines = [code_lines]
        
        full_code = "\n".join(code_lines)
        
        print("#" * 100)
        print("#########################code#########################")
        print(full_code)
        print("#" * 100)


        
        # Use Modal's native execution methods
        response = self._python_executor(full_code, self._globals_dict, self._locals_dict)
        
        print("!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!<response>!!!!!!!!!!!!!!!!!!!!!!!!!")
        
        # Update the instance globals and locals with the execution results
        self._globals_dict = cloudpickle.loads(make_session_blob(response["updated_globals"]))
        self._locals_dict = cloudpickle.loads(make_session_blob(response["updated_locals"]))

        
        self._log_response(response)
        
        return clean_response(response)
    
    def _python_executor(self, code: str, globals_dict: Dict[str, Any] = None, locals_dict: Dict[str, Any] = None):
        """Execute Python code using Modal's native .local() or .remote() methods."""
        execution_mode = "🏠 LOCALLY" if self.local_execution else "☁️ REMOTELY"
        print(f"Executing code {execution_mode} via Modal")
        
        # Prepare the full code with default codes if needed
        if self.executed_default_codes:
            print("✔️ default codes already executed")
            full_code = "\n".join(self.code_tools_definitions) +"\n\n"+code
            # Code tools and default code are trusted, user code is not
        else:
            full_code = "\n".join(self.code_tools_definitions) +"\n\n"+ "\n".join(self.default_python_codes) + "\n\n" + code
            self.executed_default_codes = True
            # First execution includes framework code which is trusted
        
        # Use Modal's native execution methods
        if self.local_execution:
            return self._app_run_python.local(
                full_code,
                globals_dict or {},
                locals_dict or {},
                self.authorized_imports,
                self.is_trusted_code,
            )
        else:
            with self.app.run():
                return self._app_run_python.remote(
                    full_code,
                    globals_dict or {},
                    locals_dict or {},
                    self.authorized_imports,
                    self.is_trusted_code,
                )
    
    def _log_response(self, response: Dict[str, Any]):
        """Log the response from code execution."""
        execution_mode = "🏠 LOCAL" if self.local_execution else "☁️ REMOTE"
        print(f"#########################{execution_mode} EXECUTION#########################")
        print("#########################<printed_output>#########################")
        print(response["printed_output"])
        print("#########################</printed_output>#########################")
        if response.get("return_value",None) not in [None,""]:
            print("#########################<return_value>#########################")
            print(response["return_value"])
            print("#########################</return_value>#########################")
        if response.get("stderr",None) not in [None,""]:
            print("#########################<stderr>#########################")
            print(response["stderr"])
            print("#########################</stderr>#########################")
        if response.get("error_traceback",None) not in [None,""]:
            print("#########################<traceback>#########################")
            # Check if this is a security exception and highlight it in red if so
            error_text = response["error_traceback"]
            if "SECURITY" in error_text:
                try:
                    from ..modal_sandbox import COLOR
                except ImportError:
                    # Fallback colors if modal_sandbox is not available
                    COLOR = {
                        "RED": "\033[91m",
                        "ENDC": "\033[0m",
                    }
                print(f"{COLOR['RED']}{error_text}{COLOR['ENDC']}")
            else:
                print(error_text)
            print("#########################</traceback>#########################")
    
    async def cleanup(self):
        """Clean up Modal resources."""
        # Modal handles cleanup automatically, but we can reset state
        self.executed_default_codes = False
        self._globals_dict = {}
        self._locals_dict = {} 