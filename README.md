# Task-Management-Copilot

#### **Overview**
This project is an **AI-powered Asana task manager** that integrates **OpenAI's GPT-4** with **Asana's API** to streamline task management using natural language commands. Users can create, list, complete, and delete tasks effortlessly through conversational inputs. The AI interprets the command and automates task actions inside Asana.

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
- **Asana API** 🔗
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
1. Clone the repository:
   ```bash
   git clone https://github.com/your-repo/AI-Asana-Task-Manager.git
   cd AI-Asana-Task-Manager
   ```
2. Install dependencies:
   ```bash
   pip install requests openai
   ```
3. Configure **Asana API Key** in the script.
4. Run the program:
   ```bash
   python task_manager.py
   ```

#### **Future Enhancements**
- 🏗 **Voice Command Integration** using speech-to-text.
- 📆 **Task Scheduling & Reminders** using AI predictions.
- 📊 **Project Analytics Dashboard** for task tracking.


