from todo_cli.storage import load_data, save_data
from todo_cli.utils import colored_status, colored_priority, format_due_date, validate_priority
from colorama import Fore, Style


def add_todo(task, priority, tag, due):
    if not validate_priority(priority):
        print(f"{Fore.RED}Invalid priority. Choose from low, medium, or high.{Style.RESET_ALL}")
        return

    todos = load_data()
    todos.append({
        "task": task,
        "done": False,
        "priority": priority,
        "tag": tag,
        "due": due,
    })
    save_data(todos)
    print(f"{Fore.GREEN}Added:{Style.RESET_ALL} {task}")


def list_todos(filter_type="all", tag=None, search=None):
    todos = load_data()

    for i, todo in enumerate(todos):
        if filter_type == "done" and not todo["done"]:
            continue
        if filter_type == "pending" and todo["done"]:
            continue
        if tag and (todo.get("tag") or "").lower() != tag.lower():
            continue
        if search and search.lower() not in todo["task"].lower():
            continue

        status = colored_status(todo["done"])
        priority = colored_priority(todo.get("priority", "low"))
        due = format_due_date(todo.get("due"))
        tag_str = todo.get("tag", "-")

        print(f"{i}: [{status}] {todo['task']} - {priority} {due} [Tag: {tag_str}]")


def mark_done(index):
    todos = load_data()
    if index < 0 or index >= len(todos):
        print(f"{Fore.RED}Invalid index{Style.RESET_ALL}")
        return

    todos[index]["done"] = True
    save_data(todos)
    print(f"{Fore.GREEN}Marked as done:{Style.RESET_ALL} {todos[index]['task']}")


def delete_todo(index):
    todos = load_data()
    if index < 0 or index >= len(todos):
        print(f"{Fore.RED}Invalid index{Style.RESET_ALL}")
        return

    task = todos.pop(index)
    save_data(todos)
    print(f"{Fore.YELLOW}Deleted:{Style.RESET_ALL} {task['task']}")


def edit_todo(index, new_task):
    todos = load_data()
    if index < 0 or index >= len(todos):
        print(f"{Fore.RED}Invalid index{Style.RESET_ALL}")
        return

    old_task = todos[index]["task"]
    todos[index]["task"] = new_task
    save_data(todos)
    print(f"{Fore.BLUE}Updated task {index}:{Style.RESET_ALL} '{old_task}' → '{new_task}'")
