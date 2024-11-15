# Task queue for spam check activities
TASK_QUEUE_COMSES_SPAM_CHECK = "spam_check_queue"
TASK_QUEUE_OLLAMA = "ollama_queue"

# Workflow IDs
DFS_WID_CHECK_SPAM = "check_spam_workflow"
DFS_WID_GET_SPAM_REPORT = "get_spam_report_workflow"

# Activity names
UFS_ACTIVITY_GET_LATEST_BATCH = "get_latest_batch_from_comses"
UFS_ACTIVITY_CHAT_WITH_LLM = "generate_llm_spam_report"
UFS_ACTIVITY_SEND_SPAM_REPORT = "send_spam_report_to_comses"

# Retry policy constants
INITIAL_INTERVAL_SECONDS = 1
MAXIMUM_INTERVAL_SECONDS = 10
MAXIMUM_ATTEMPTS = 3

# Timeout constants
ACTIVITY_TIMEOUT_SECONDS = 300  # 5 minutes
CHILD_WORKFLOW_TIMEOUT_SECONDS = 600  # 10 minutes

# LLM model name (this could be an environment variable)
LLM_MODEL_NAME = "gpt-3.5-turbo"  # or whatever model you're using

# Maximum number of parallel child workflows
MAX_PARALLEL_WORKFLOWS = 10
