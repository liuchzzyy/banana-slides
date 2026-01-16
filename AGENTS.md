# 🍌 Banana Slides - AI Agent Architecture

This project leverages a multi-agent system to handle complex PPT generation tasks. Below is the documentation of the agentic workflow and architecture.

## 🤖 Core Agents

### 1. **Plan Agent**
- **Role**: Strategic Planner
- **Responsibilities**:
  - Analyzes user requests.
  - Breaks down complex tasks into actionable steps (todo list).
  - Orchestrates the execution flow.

### 2. **Explore Agent** (Contextual Grep)
- **Role**: Codebase Researcher
- **Responsibilities**:
  - Navigates the project structure.
  - Finds relevant code patterns and implementations.
  - Provides context to other agents.

### 3. **Librarian Agent** (Reference Grep)
- **Role**: External Knowledge Expert
- **Responsibilities**:
  - Searches external documentation (OpenAI, Python libs).
  - Finds usage examples and best practices.
  - Ensures compliance with external API standards.

### 4. **Oracle Agent**
- **Role**: Senior Architect / Reasoning Engine
- **Responsibilities**:
  - Makes high-level architectural decisions.
  - Solves complex debugging issues.
  - Performs code review and quality assurance.

## 🔄 Workflow

1.  **Intent Analysis**: The system first analyzes the user's request to determine the intent (e.g., refactor, feature addition, debugging).
2.  **Exploration**: Background agents (`explore`, `librarian`) are spawned to gather necessary context and external knowledge.
3.  **Planning**: The `Plan Agent` creates a detailed todo list based on the gathered context.
4.  **Execution**: The system executes the plan, utilizing specialized tools (CLI, file operations) and sub-agents as needed.
5.  **Verification**: Changes are verified against requirements (e.g., via CLI tests).

## 🛠️ Tooling Integration

-   **CLI**: The primary interface for interaction (`banana-slides` command).
-   **UV**: Modern Python package management for fast and reliable dependency resolution.
-   **OpenAI/Gemini**: Underlying LLM providers for content generation.

## 📝 Contribution

When contributing, consider how your changes affect the agentic workflow. Ensure clear documentation and consistent code patterns to help agents understand and modify the codebase effectively.
