"""
Qubots Playground Integration Module

Provides standardized interfaces for integrating qubots with the Rastion platform playground.
Handles result formatting, progress reporting, and error management for web-based optimization.
"""

import json
import time
import traceback
import inspect
from typing import Dict, Any, Optional, Union, List, Callable
from datetime import datetime
from dataclasses import dataclass, asdict
from enum import Enum

from .base_problem import BaseProblem
from .base_optimizer import BaseOptimizer
from .rastion_client import get_global_client
from .rastion import load_qubots_model
from .dashboard import QubotsAutoDashboard, DashboardResult


def _make_json_serializable(obj: Any) -> Any:
    """
    Convert objects to JSON-serializable format.
    Handles enums, dataclasses, and other common non-serializable types.
    """
    if isinstance(obj, Enum):
        return obj.value
    elif hasattr(obj, 'to_dict') and callable(obj.to_dict):
        return obj.to_dict()
    elif hasattr(obj, '__dict__'):
        return {k: _make_json_serializable(v) for k, v in obj.__dict__.items()}
    elif isinstance(obj, (list, tuple)):
        return [_make_json_serializable(item) for item in obj]
    elif isinstance(obj, dict):
        return {k: _make_json_serializable(v) for k, v in obj.items()}
    elif isinstance(obj, (str, int, float, bool, type(None))):
        return obj
    else:
        # For other types, try to convert to string
        return str(obj)


@dataclass
class PlaygroundResult:
    """Standardized result format for playground optimization runs."""
    success: bool
    problem_name: str
    optimizer_name: str
    problem_username: str
    optimizer_username: str
    execution_time: float
    timestamp: str
    best_solution: Optional[List[float]] = None
    best_value: Optional[float] = None
    iterations: Optional[int] = None
    history: Optional[List[Dict[str, Any]]] = None
    metadata: Optional[Dict[str, Any]] = None
    error_message: Optional[str] = None
    error_type: Optional[str] = None

    # Leaderboard submission support
    leaderboard_eligible: bool = False
    standardized_problem_id: Optional[int] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        result_dict = asdict(self)
        return _make_json_serializable(result_dict)


@dataclass
class ModelInfo:
    """Information about a qubots model for playground display."""
    name: str
    username: str
    description: str
    model_type: str  # 'problem' or 'optimizer'
    repository_url: str
    last_updated: str
    tags: List[str]
    metadata: Dict[str, Any]


class PlaygroundExecutor:
    """
    Handles execution of qubots optimizations for the playground interface.
    Provides standardized result formatting and error handling with real-time logging.
    """

    def __init__(self,
                 progress_callback: Optional[Callable[[str, float], None]] = None,
                 log_callback: Optional[Callable[[str, str, str], None]] = None):
        """
        Initialize the playground executor.

        Args:
            progress_callback: Optional callback for progress updates (message, progress_percent)
            log_callback: Optional callback for real-time logs (level, message, source)
        """
        self.progress_callback = progress_callback
        self.log_callback = log_callback
        self.client = get_global_client()

    def execute_optimization(self,
                           problem_name: str,
                           optimizer_name: str,
                           problem_username: Optional[str] = None,
                           optimizer_username: Optional[str] = None,
                           problem_params: Optional[Dict[str, Any]] = None,
                           optimizer_params: Optional[Dict[str, Any]] = None) -> PlaygroundResult:
        """
        Execute an optimization using qubots models from the Rastion platform.

        Args:
            problem_name: Name of the problem repository
            optimizer_name: Name of the optimizer repository
            problem_username: Username of problem owner (auto-detected if None)
            optimizer_username: Username of optimizer owner (auto-detected if None)
            problem_params: Optional parameters to override problem defaults
            optimizer_params: Optional parameters to override optimizer defaults

        Returns:
            PlaygroundResult with execution details and results
        """
        start_time = time.time()
        timestamp = datetime.now().isoformat()

        try:
            # Report progress and log start
            self._log('info', 'Starting optimization execution...', 'system')
            self._report_progress("Loading problem model...", 10)

            # Load problem with parameter overrides
            self._log('info', f'Loading problem: {problem_username}/{problem_name}', 'loader')
            if problem_params:
                self._log('info', f'Applying problem parameters: {problem_params}', 'config')

            # Handle standardized problems
            if problem_name.startswith("standardized_") and problem_username == "standardized":
                self._log('info', f'Loading standardized benchmark problem: {problem_name}', 'loader')
                problem = self._load_standardized_problem(problem_name, problem_params)
            else:
                problem = load_qubots_model(problem_name, problem_username, override_params=problem_params)

            if not isinstance(problem, BaseProblem):
                raise ValueError(f"Model {problem_name} is not a valid problem")
            self._log('info', f'Problem loaded successfully: {type(problem).__name__}', 'loader')

            self._report_progress("Loading optimizer model...", 30)

            # Load optimizer with parameter overrides
            self._log('info', f'Loading optimizer: {optimizer_username}/{optimizer_name}', 'loader')
            if optimizer_params:
                self._log('info', f'Applying optimizer parameters: {optimizer_params}', 'config')
            optimizer = load_qubots_model(optimizer_name, optimizer_username, override_params=optimizer_params)
            if not isinstance(optimizer, BaseOptimizer):
                raise ValueError(f"Model {optimizer_name} is not a valid optimizer")
            self._log('info', f'Optimizer loaded successfully: {type(optimizer).__name__}', 'loader')

            self._report_progress("Running optimization...", 50)

            # Execute optimization with progress callback
            self._log('info', 'Starting optimization algorithm...', 'optimizer')

            # Create progress callback for real-time logging
            progress_callback = self._create_optimization_progress_callback()

            # Pass both progress_callback and log_callback to optimizer
            result = optimizer.optimize(problem, progress_callback=progress_callback, log_callback=self.log_callback)

            self._log('info', f'Optimization completed! Best value: {result.best_value:.6f}', 'optimizer')
            if hasattr(result, 'iterations'):
                self._log('info', f'Total iterations: {result.iterations}', 'optimizer')
            if hasattr(result, 'runtime_seconds'):
                self._log('info', f'Runtime: {result.runtime_seconds:.3f} seconds', 'optimizer')

            self._report_progress("Processing results...", 90)

            # Extract results in standardized format
            execution_time = time.time() - start_time
            self._log('info', f'Total execution time: {execution_time:.3f} seconds', 'system')

            # Handle different result formats
            if hasattr(result, 'best_solution'):
                best_solution = result.best_solution
                best_value = getattr(result, 'best_value', None) or getattr(result, 'best_fitness', None)
            elif isinstance(result, dict):
                best_solution = result.get('best_solution')
                best_value = result.get('best_value') or result.get('best_fitness')
            else:
                best_solution = None
                best_value = None

            # Extract iteration history if available
            history = None
            iterations = None
            if hasattr(result, 'history'):
                history = result.history
                iterations = len(history) if history else None
                if iterations:
                    self._log('info', f'Optimization history contains {iterations} entries', 'results')
            elif isinstance(result, dict) and 'history' in result:
                history = result['history']
                iterations = len(history) if history else None
                if iterations:
                    self._log('info', f'Optimization history contains {iterations} entries', 'results')

            # Collect metadata with proper JSON serialization
            problem_metadata = getattr(problem, 'metadata', {})
            optimizer_metadata = getattr(optimizer, 'metadata', {})

            metadata = {
                'problem_class': problem.__class__.__name__,
                'optimizer_class': optimizer.__class__.__name__,
                'problem_metadata': _make_json_serializable(problem_metadata),
                'optimizer_metadata': _make_json_serializable(optimizer_metadata),
                'result_type': type(result).__name__
            }

            self._log('info', 'Results processed successfully', 'system')
            self._report_progress("Complete!", 100)

            return PlaygroundResult(
                success=True,
                problem_name=problem_name,
                optimizer_name=optimizer_name,
                problem_username=problem_username or "unknown",
                optimizer_username=optimizer_username or "unknown",
                execution_time=execution_time,
                timestamp=timestamp,
                best_solution=best_solution,
                best_value=best_value,
                iterations=iterations,
                history=history,
                metadata=metadata
            )

        except Exception as e:
            execution_time = time.time() - start_time
            error_message = str(e)
            error_type = type(e).__name__

            # Log error details
            self._log('error', f'Optimization failed: {error_message}', 'system')
            self._log('error', f'Error type: {error_type}', 'system')

            # Log full traceback for debugging
            traceback_str = traceback.format_exc()
            print(f"Playground execution error: {traceback_str}")
            self._log('debug', f'Full traceback: {traceback_str}', 'system')

            return PlaygroundResult(
                success=False,
                problem_name=problem_name,
                optimizer_name=optimizer_name,
                problem_username=problem_username or "unknown",
                optimizer_username=optimizer_username or "unknown",
                execution_time=execution_time,
                timestamp=timestamp,
                error_message=error_message,
                error_type=error_type
            )

    def _report_progress(self, message: str, progress: float):
        """Report progress if callback is available."""
        if self.progress_callback:
            self.progress_callback(message, progress)

    def _log(self, level: str, message: str, source: str = "qubots"):
        """Log a message if callback is available."""
        if self.log_callback:
            self.log_callback(level, message, source)
        # Also print to console for debugging
        print(f"[{level.upper()}] [{source}] {message}")

    def _create_optimization_progress_callback(self):
        """Create a progress callback for optimization that logs progress."""
        def progress_callback(progress_data: Dict[str, Any]):
            iteration = progress_data.get('iteration', 0)
            best_value = progress_data.get('best_value', 0)

            # Log iteration progress
            self._log('info', f"Iteration {iteration}: Best value = {best_value:.6f}", "optimizer")

            # Log additional metrics if available
            for key, value in progress_data.items():
                if key not in ['iteration', 'best_value', 'optimizer_id']:
                    if isinstance(value, (int, float)):
                        self._log('debug', f"{key}: {value:.6f}", "metrics")
                    else:
                        self._log('debug', f"{key}: {value}", "metrics")

            # Report overall progress
            if self.progress_callback:
                progress_percent = min(100, (iteration / 1000) * 100)  # Estimate based on iteration
                self._report_progress(f"Iteration {iteration}", progress_percent)

        return progress_callback

    def _load_standardized_problem(self, problem_name: str, problem_params: Optional[Dict[str, Any]] = None):
        """Load a standardized benchmark problem."""
        try:
            from .standardized_benchmarks import StandardizedBenchmarkRegistry

            # Extract problem type and ID from name (format: standardized_{type}_{id})
            parts = problem_name.split('_')
            if len(parts) >= 3:
                problem_type = parts[1]
                problem_id = int(parts[2])

                # Get benchmark specs and find the matching one
                specs = StandardizedBenchmarkRegistry.get_benchmark_specs()

                # Find spec by ID (1-based indexing)
                if 1 <= problem_id <= len(specs):
                    spec = specs[problem_id - 1]
                    self._log('info', f'Creating standardized problem: {spec.name}', 'loader')

                    # Create the problem instance
                    problem = StandardizedBenchmarkRegistry.create_problem(spec)

                    # Apply any parameter overrides if provided
                    if problem_params:
                        self._log('info', f'Applying parameter overrides to standardized problem', 'config')
                        # Note: Standardized problems may have limited parameter override support

                    return problem
                else:
                    raise ValueError(f"Standardized problem ID {problem_id} not found")
            else:
                raise ValueError(f"Invalid standardized problem name format: {problem_name}")

        except Exception as e:
            self._log('error', f'Failed to load standardized problem {problem_name}: {str(e)}', 'loader')
            raise

    def submit_to_leaderboard(self,
                            result: PlaygroundResult,
                            solver_repository: str,
                            solver_config: Dict[str, Any],
                            solver_version: Optional[str] = None) -> Optional[Dict[str, Any]]:
        """
        Submit a playground result to the leaderboard if eligible.

        Args:
            result: PlaygroundResult from optimization
            solver_repository: Repository path for the solver
            solver_config: Configuration used for the solver
            solver_version: Version/commit hash of the solver

        Returns:
            Submission result or None if not eligible
        """
        if not result.success or not result.leaderboard_eligible or not result.standardized_problem_id:
            return None

        try:
            # Import here to avoid circular imports
            from .leaderboard import LeaderboardIntegration

            # Create leaderboard integration
            leaderboard = LeaderboardIntegration()

            # Create optimization result object
            from .base_optimizer import OptimizationResult
            opt_result = OptimizationResult(
                best_solution=result.best_solution,
                best_value=result.best_value,
                is_feasible=True,
                runtime_seconds=result.execution_time,
                iterations=result.iterations,
                termination_reason="completed"
            )

            # Submit to leaderboard
            submission_result = leaderboard.submit_optimization_result(
                result=opt_result,
                problem_id=result.standardized_problem_id,
                solver_name=result.optimizer_name,
                solver_repository=solver_repository,
                solver_config=solver_config,
                solver_version=solver_version
            )

            self._log('info', f'Successfully submitted to leaderboard: {submission_result.get("id", "unknown")}', 'leaderboard')
            return submission_result

        except Exception as e:
            self._log('error', f'Failed to submit to leaderboard: {str(e)}', 'leaderboard')
            return None


# Convenience functions for direct use
def execute_playground_optimization(problem_name: str = None,
                                  optimizer_name: str = None,
                                  problem_username: Optional[str] = None,
                                  optimizer_username: Optional[str] = None,
                                  # Directory-based execution parameters
                                  problem_dir: Optional[str] = None,
                                  optimizer_dir: Optional[str] = None,
                                  # Logging callback for real-time output
                                  log_callback: Optional[Callable[[str, str, str], None]] = None,
                                  **kwargs) -> Dict[str, Any]:
    """
    Convenience function to execute optimization and return dashboard result as dictionary.
    Uses qubots built-in dashboard and visualization capabilities.

    Supports two modes:
    1. Name-based: Load models by name from Rastion platform
    2. Directory-based: Load models from local directories
    """
    try:
        # Create executor with logging support
        executor = PlaygroundExecutor(log_callback=log_callback)

        # Determine execution mode
        if problem_dir is not None and optimizer_dir is not None:
            # Directory-based execution mode
            if log_callback:
                log_callback('info', f'Loading models from directories: {problem_dir}, {optimizer_dir}', 'system')

            # Get parameters for directory-based loading
            problem_params = kwargs.get('problem_params', {})
            optimizer_params = kwargs.get('optimizer_params', {})

            problem = _load_model_from_directory(problem_dir, "problem", override_params=problem_params)
            optimizer = _load_model_from_directory(optimizer_dir, "optimizer", override_params=optimizer_params)

            # Use directory names as display names if not provided
            if problem_name is None:
                from pathlib import Path
                problem_name = Path(problem_dir).name
            if optimizer_name is None:
                from pathlib import Path
                optimizer_name = Path(optimizer_dir).name

        elif problem_name is not None and optimizer_name is not None:
            # Name-based execution mode - use the executor for consistent logging
            result = executor.execute_optimization(
                problem_name=problem_name,
                optimizer_name=optimizer_name,
                problem_username=problem_username,
                optimizer_username=optimizer_username,
                problem_params=kwargs.get('problem_params', {}),
                optimizer_params=kwargs.get('optimizer_params', {})
            )

            # Convert PlaygroundResult to dashboard format
            dashboard_dict = result.to_dict()
            if result.success:
                dashboard_dict.update({
                    'dashboard': {
                        'plots': [],
                        'metrics': {
                            'best_value': result.best_value,
                            'iterations': result.iterations,
                            'execution_time': result.execution_time
                        }
                    }
                })

            return dashboard_dict

        else:
            raise ValueError("Either provide (problem_name, optimizer_name) or (problem_dir, optimizer_dir)")

        # Run optimization with automatic dashboard generation
        if log_callback:
            log_callback('info', 'Running optimization with dashboard generation...', 'system')

        dashboard_result = QubotsAutoDashboard.auto_optimize_with_dashboard(
            problem=problem,
            optimizer=optimizer,
            problem_name=problem_name,
            optimizer_name=optimizer_name,
            log_callback=log_callback
        )

        return dashboard_result.to_dict()

    except Exception as e:
        # Return error dashboard result
        import traceback
        error_result = DashboardResult(
            success=False,
            problem_name=problem_name or "unknown",
            optimizer_name=optimizer_name or "unknown",
            execution_time=0.0,
            error_message=str(e)
        )
        result_dict = error_result.to_dict()
        result_dict["traceback"] = traceback.format_exc()
        return result_dict


def _load_model_from_directory(directory: str, expected_type: str, override_params: Optional[Dict[str, Any]] = None):
    """
    Load a qubots model from a directory containing qubot.py and config.json.

    Args:
        directory: Path to the directory
        expected_type: Expected model type ("problem" or "optimizer")
        override_params: Parameters to override during model instantiation

    Returns:
        Loaded model instance
    """
    import sys
    import json
    import importlib.util
    from pathlib import Path

    directory = Path(directory)
    if not directory.exists():
        raise ValueError(f"Directory does not exist: {directory}")

    # Load config.json
    config_path = directory / "config.json"
    if not config_path.exists():
        raise ValueError(f"config.json not found in {directory}")

    with open(config_path, 'r', encoding='utf-8') as f:
        config = json.load(f)

    # Validate type
    model_type = config.get("type")
    if model_type != expected_type:
        raise ValueError(f"Expected type='{expected_type}' in config.json, got '{model_type}'")

    # Load the module
    qubot_path = directory / "qubot.py"
    if not qubot_path.exists():
        raise ValueError(f"qubot.py not found in {directory}")

    # Add directory to Python path temporarily
    sys.path.insert(0, str(directory))
    try:
        # Import the module
        spec = importlib.util.spec_from_file_location("qubot", qubot_path)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)

        # Get the class
        class_name = config.get("class_name")
        if not class_name:
            raise ValueError("class_name not found in config.json")

        if not hasattr(module, class_name):
            raise ValueError(f"Class '{class_name}' not found in qubot.py")

        model_class = getattr(module, class_name)

        # Create instance with default parameters and overrides
        default_params = config.get("default_params", {})
        if override_params:
            default_params.update(override_params)
        model_instance = model_class(**default_params)

        return model_instance

    finally:
        # Remove directory from Python path
        if str(directory) in sys.path:
            sys.path.remove(str(directory))


def extract_parameter_schema(model: Union[BaseProblem, BaseOptimizer]) -> Dict[str, Any]:
    """
    Extract parameter schema from a qubots model for dynamic UI generation.

    Args:
        model: BaseProblem or BaseOptimizer instance

    Returns:
        Dictionary containing parameter schema information
    """
    schema = {
        "model_type": "problem" if isinstance(model, BaseProblem) else "optimizer",
        "model_name": getattr(model.metadata, 'name', model.__class__.__name__),
        "parameters": {}
    }

    if isinstance(model, BaseOptimizer):
        # Extract from optimizer metadata
        metadata = model._metadata
        param_info = model.get_parameter_info()

        # Process required parameters
        for param in metadata.required_parameters:
            param_schema = {
                "required": True,
                "type": "string",  # Default type
                "description": f"Required parameter: {param}"
            }

            # Add range information if available
            if param in metadata.parameter_ranges:
                min_val, max_val = metadata.parameter_ranges[param]
                param_schema.update({
                    "type": "number",
                    "minimum": min_val,
                    "maximum": max_val
                })

            # Add current value if available
            if param in param_info.get("current_values", {}):
                param_schema["default"] = param_info["current_values"][param]

            schema["parameters"][param] = param_schema

        # Process optional parameters
        for param in metadata.optional_parameters:
            param_schema = {
                "required": False,
                "type": "string",  # Default type
                "description": f"Optional parameter: {param}"
            }

            # Add range information if available
            if param in metadata.parameter_ranges:
                min_val, max_val = metadata.parameter_ranges[param]
                param_schema.update({
                    "type": "number",
                    "minimum": min_val,
                    "maximum": max_val
                })

            # Add current value if available
            if param in param_info.get("current_values", {}):
                param_schema["default"] = param_info["current_values"][param]

            schema["parameters"][param] = param_schema

    elif isinstance(model, BaseProblem):
        # Extract from problem metadata and constructor
        metadata = model._metadata

        # Try to extract parameters from constructor signature
        try:
            sig = inspect.signature(model.__class__.__init__)
            for param_name, param in sig.parameters.items():
                if param_name == 'self':
                    continue

                param_schema = {
                    "required": param.default == inspect.Parameter.empty,
                    "type": "string",  # Default type
                    "description": f"Problem parameter: {param_name}"
                }

                # Try to infer type from default value
                if param.default != inspect.Parameter.empty:
                    param_schema["default"] = param.default
                    if isinstance(param.default, (int, float)):
                        param_schema["type"] = "number"
                    elif isinstance(param.default, bool):
                        param_schema["type"] = "boolean"
                    elif isinstance(param.default, list):
                        param_schema["type"] = "array"

                # Add bounds information if available in metadata
                if metadata.variable_bounds and param_name in metadata.variable_bounds:
                    min_val, max_val = metadata.variable_bounds[param_name]
                    param_schema.update({
                        "type": "number",
                        "minimum": min_val,
                        "maximum": max_val
                    })

                schema["parameters"][param_name] = param_schema

        except Exception as e:
            # Fallback: add common problem parameters
            schema["parameters"]["dimension"] = {
                "required": False,
                "type": "number",
                "description": "Problem dimension",
                "minimum": 1,
                "default": metadata.dimension or 10
            }

    return schema


def get_model_parameter_schema(model_name: str,
                              username: Optional[str] = None) -> Dict[str, Any]:
    """
    Load a model and extract its parameter schema.

    Args:
        model_name: Name of the model repository
        username: Repository owner (auto-detected if None)

    Returns:
        Parameter schema dictionary
    """
    try:
        model = load_qubots_model(model_name, username)
        return extract_parameter_schema(model)
    except Exception as e:
        return {
            "error": str(e),
            "model_name": model_name,
            "parameters": {}
        }