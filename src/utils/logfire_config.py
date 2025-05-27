import logfire

# Initialize Logfire
logfire.configure()

# Example of structured logging
def log_step_start(step_name: str, context: dict = None):
    """Logs the start of a pipeline step with context."""
    logfire.info("Starting step: {step_name}", step_name=step_name, **(context or {}))

def log_step_end(step_name: str, status: str, context: dict = None):
    """Logs the end of a pipeline step with status and context."""
    logfire.info("Step {step_name} finished with status: {status}", step_name=step_name, status=status, **(context or {}))

def log_step_error(step_name: str, error: Exception, context: dict = None):
    """Logs an error during a pipeline step with exception details and context."""
    logfire.error("Error during step {step_name}: {error}", step_name=step_name, error=error, exc_info=True, **(context or {}))