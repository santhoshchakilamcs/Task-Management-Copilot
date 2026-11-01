"""Task Management Copilot CLI.

A command-line version of the logic in Task_Management_Copilot.ipynb,
with no behaviour change to the Asana actions themselves:
create, list, complete, and delete tasks, plus a natural-language
``process`` mode that uses GPT-4 to parse a command into one of
those actions, exactly as the notebook does.

Configuration is by environment variable only. No API key and no
workspace ID is hardcoded here, and no real Asana workspace is used
by this file on its own:

- ASANA_API_KEY: your Asana personal access token
- ASANA_BASE_URL: default https://app.asana.com/api/1.0
- ASANA_WORKSPACE_ID: required for list/create/complete/delete
- OPENAI_API_KEY: required only for ``process`` mode (GPT-4 parsing)

Examples (do not run these against a real workspace unless you
intend to change it):

    python task_copilot.py list --project "Marketing"
    python task_copilot.py create --project "Marketing" --task "Report submission" --due-date 2026-11-07
    python task_copilot.py process --text "Create a task for report submission in Marketing project by Friday."
    python task_copilot.py repl
"""

import argparse
import json
import os
import sys

import requests

BASE_URL = os.environ.get("ASANA_BASE_URL", "https://app.asana.com/api/1.0")
WORKSPACE_ID = os.environ.get("ASANA_WORKSPACE_ID", "")


def _headers():
    key = os.environ.get("ASANA_API_KEY", "")
    if not key:
        raise SystemExit("ASANA_API_KEY is not set. Export it before running this CLI.")
    return {"Authorization": f"Bearer {key}", "Content-Type": "application/json"}


def _workspace_id(args):
    wid = getattr(args, "workspace", "") or WORKSPACE_ID
    if not wid:
        raise SystemExit("Workspace ID is required: pass --workspace or set ASANA_WORKSPACE_ID.")
    return wid


def get_project_id_by_name(workspace_id, project_name):
    url = f"{BASE_URL}/projects?workspace={workspace_id}"
    response = requests.get(url, headers=_headers())
    if response.status_code == 200:
        for project in response.json().get("data", []):
            if project.get("name", "").lower() == project_name.lower():
                return project.get("gid")
        return None
    print(f"Error fetching projects: {response.status_code} {response.text}")
    return None


def get_task_id_by_name(project_id, task_name):
    url = f"{BASE_URL}/projects/{project_id}/tasks"
    response = requests.get(url, headers=_headers())
    if response.status_code == 200:
        for task in response.json().get("data", []):
            if task.get("name", "").lower() == task_name.lower():
                return task.get("gid")
        return None
    print(f"Error fetching tasks: {response.status_code} {response.text}")
    return None


def create_task(name, workspace_id, project_id, assignee=None, due_date=None):
    url = f"{BASE_URL}/tasks"
    data = {"data": {"name": name, "workspace": workspace_id,
                     "projects": [project_id], "assignee": assignee,
                     "due_on": due_date}}
    response = requests.post(url, headers=_headers(), json=data)
    if response.status_code == 201:
        print("Task created successfully:", response.json())
        return response.json()
    print(f"Error creating task: {response.status_code} {response.text}")
    return None


def list_tasks(project_id):
    url = f"{BASE_URL}/projects/{project_id}/tasks"
    response = requests.get(url, headers=_headers())
    if response.status_code == 200:
        tasks = response.json().get("data", [])
        if tasks:
            return "\n".join([f"- {t['name']} (ID: {t['gid']})" for t in tasks])
        return "No tasks found."
    return f"Error fetching tasks: {response.json()}"


def list_tasks_by_project_name(workspace_id, project_name):
    project_id = get_project_id_by_name(workspace_id, project_name)
    if not project_id:
        return f"Project '{project_name}' not found in workspace {workspace_id}."
    return list_tasks(project_id)


def delete_task(task_id):
    url = f"{BASE_URL}/tasks/{task_id}"
    response = requests.delete(url, headers=_headers())
    if response.status_code == 200:
        return "Task deleted successfully."
    return f"Error deleting task: {response.status_code} {response.text}"


def delete_task_by_name(workspace_id, project_name, task_name):
    project_id = get_project_id_by_name(workspace_id, project_name)
    if not project_id:
        return f"Project '{project_name}' not found."
    task_id = get_task_id_by_name(project_id, task_name)
    if not task_id:
        return f"Task '{task_name}' not found in project '{project_name}'."
    return delete_task(task_id)


def complete_task(task_id):
    url = f"{BASE_URL}/tasks/{task_id}"
    data = {"data": {"completed": True}}
    response = requests.put(url, headers=_headers(), json=data)
    if response.status_code == 200:
        return "Task marked as complete successfully."
    return f"Error marking task as complete: {response.status_code} {response.text}"


def complete_task_by_name(workspace_id, project_name, task_name):
    project_id = get_project_id_by_name(workspace_id, project_name)
    if not project_id:
        return f"Project '{project_name}' not found in workspace {workspace_id}."
    task_id = get_task_id_by_name(project_id, task_name)
    if not task_id:
        return f"Task '{task_name}' not found in project '{project_name}'."
    return complete_task(task_id)


# Session state, mirroring the notebook.
session_state = {"current_project": None, "tasks": {}}


def process_command(command, workspace_id):
    """Parse a natural-language command with GPT-4, as in the notebook.

    System prompt and output keys (action, project_name, task_name,
    assignee, due_date) match Task_Management_Copilot.ipynb. This
    requires the openai 0.28-style ChatCompletion API used there and
    OPENAI_API_KEY in the environment.
    """
    try:
        import openai
    except ImportError:
        return "Error processing command: openai package is not installed (notebook pins openai==0.28)."
    openai.api_key = os.environ.get("OPENAI_API_KEY", "")
    if not openai.api_key:
        return "Error processing command: OPENAI_API_KEY is not set."
    messages = [
        {"role": "system", "content": "You are an assistant for managing Asana tasks."},
        {"role": "user", "content": f"""
        Based on the user command, determine whether to create a task, list tasks in a project, mark a task as complete, or delete a task.
        Assume the context of the current project if one exists; otherwise, prompt for the project name.
        User command: "{command}"

        Return a JSON object with keys: action (create, list, complete, delete), project_name, task_name, assignee, and due_date. Leave irrelevant keys empty.
        """},
    ]
    try:
        response = openai.ChatCompletion.create(
            model="gpt-4", messages=messages, temperature=0.7, max_tokens=200)
        result = json.loads(response["choices"][0]["message"]["content"].strip())
    except Exception as e:
        return f"Error processing command: {e}"

    action = result.get("action")
    project_name = result.get("project_name")
    task_name = result.get("task_name")
    assignee = result.get("assignee")
    due_date = result.get("due_date")
    if not project_name and session_state["current_project"]:
        project_name = session_state["current_project"]
    if action in ["create", "list", "complete", "delete"] and project_name:
        session_state["current_project"] = project_name

    if action == "create":
        project_id = get_project_id_by_name(workspace_id, project_name)
        if not project_id:
            return f"Project '{project_name}' not found."
        return create_task(task_name, workspace_id, project_id, assignee, due_date)
    if action == "list":
        return list_tasks_by_project_name(workspace_id, project_name)
    if action == "complete":
        return complete_task_by_name(workspace_id, project_name, task_name)
    if action == "delete":
        return delete_task_by_name(workspace_id, project_name, task_name)
    return "Invalid action specified."


def repl():
    workspace_id = _workspace_id(argparse.Namespace(workspace=""))
    print("Welcome to the AI-Powered Asana Task Manager")
    while True:
        if session_state["current_project"]:
            print(f"\nCurrent project: {session_state['current_project']}")
        else:
            print("\nNo active project. Specify a project in your next command.")
        command = input("Enter your command (type 'quit' to exit): ").strip()
        if command.lower() == "quit":
            print("Goodbye! Resetting session.")
            session_state["current_project"] = None
            session_state["tasks"] = {}
            break
        print(process_command(command, workspace_id))


def main(argv=None):
    parser = argparse.ArgumentParser(description="Task Management Copilot CLI")
    parser.add_argument("--workspace", default="", help="Asana workspace ID (or ASANA_WORKSPACE_ID)")
    sub = parser.add_subparsers(dest="command", required=True)
    p = sub.add_parser("create"); p.add_argument("--project", required=True); p.add_argument("--task", required=True); p.add_argument("--assignee", default=None); p.add_argument("--due-date", default=None)
    p = sub.add_parser("list"); p.add_argument("--project", required=True)
    p = sub.add_parser("complete"); p.add_argument("--project", required=True); p.add_argument("--task", required=True)
    p = sub.add_parser("delete"); p.add_argument("--project", required=True); p.add_argument("--task", required=True)
    p = sub.add_parser("process"); p.add_argument("--text", required=True, help="Natural-language command to parse")
    sub.add_parser("repl")
    args = parser.parse_args(argv)
    if args.command == "repl":
        return repl()
    workspace_id = _workspace_id(args)
    if args.command == "create":
        project_id = get_project_id_by_name(workspace_id, args.project)
        if not project_id:
            print(f"Project '{args.project}' not found."); return 1
        create_task(args.task, workspace_id, project_id, args.assignee, args.due_date)
    elif args.command == "list":
        print(list_tasks_by_project_name(workspace_id, args.project))
    elif args.command == "complete":
        print(complete_task_by_name(workspace_id, args.project, args.task))
    elif args.command == "delete":
        print(delete_task_by_name(workspace_id, args.project, args.task))
    elif args.command == "process":
        print(process_command(args.text, workspace_id))
    return 0


if __name__ == "__main__":
    sys.exit(main())
