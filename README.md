# Task-Management-Copilot

#### **Overview**
This project is an **AI-powered task manager** that integrates **OpenAI's GPT-4** with **API** to streamline task management using natural language commands. Users can create, list, complete, and delete tasks effortlessly through conversational inputs. The AI interprets the command and automates task actions inside Asana.

#### **Features**
- ✅ **Natural Language Task Management** – Users can interact with Asana using simple commands like *"Create a task for report submission in Marketing project by Friday."*
- 🔍 **Task Retrieval** – List all tasks within a project dynamically.
- ✅ **Automated Task Completion** – Mark tasks as completed based on user input.
- ❌ **Task Deletion** – Remove tasks by specifying their names.
- 🔄 **Context-Aware Execution** – Keeps track of the active project to streamline workflows.
- 🔐 **Secure API Calls** – Uses Asana API with authentication for seamless task automation.

#### **Technologies Used**
- **Python** 🐍
- **OpenAI GPT-4** 🤖
- **Requests Library** 🌐
- **JSON Parsing** 🗄️

#### **How It Works**
1. The user enters a command like:
   ```
   Create a task "Prepare quarterly report" in the "Finance" project due on Monday.
   ```
2. The AI extracts intent (create/list/complete/delete), project name, task name, assignee, and due date.
3. The program interacts with Asana API to perform the requested action.
4. The user receives real-time confirmation of the task execution.

#### **Setup Instructions**
1. Install dependencies:
   ```bash
   pip install requests openai==0.28
   ```
2. Configure **Asana API Key** in the script.
3. Run the program:
   ```bash
   python task_manager.py
   ```

#### **Future Enhancements**
- 🏗 **Voice Command Integration** using speech-to-text.
- 📆 **Task Scheduling & Reminders** using AI predictions.
- 📊 **Project Analytics Dashboard** for task tracking.



#### **Command-Line Interface (new)**

The notebook's logic is also available as `task_copilot.py`, with
no change to the Asana actions themselves (create, list, complete,
delete, plus GPT-4 natural-language parsing in `process` mode).

```bash
pip install requests openai==0.28

# Keys and workspace come from the environment only, never hardcoded:
export ASANA_API_KEY="your-asana-token"
export ASANA_WORKSPACE_ID="your-workspace-id"
export OPENAI_API_KEY="your-openai-key"  # only needed for process mode

python task_copilot.py list --project "Marketing"
python task_copilot.py create --project "Marketing" --task "Report submission" --due-date 2026-11-07
python task_copilot.py complete --project "Marketing" --task "Report submission"
python task_copilot.py delete --project "Marketing" --task "Report submission"
python task_copilot.py process --text "Create a task for report submission in Marketing project by Friday."
python task_copilot.py repl
```

Notes, stated honestly:

- Do not run these commands against a real Asana workspace unless
  you intend to create, complete, or delete tasks there. There is
  no dry-run mode in this CLI.
- The notebook's original setup instructions mention a
  `task_manager.py` file, which is not in this repository; use
  `task_copilot.py` instead.
- The notebook pins `openai==0.28` and uses its `ChatCompletion`
  API for `process` mode; newer OpenAI libraries use a different
  API and may not work with that code path without changes.
