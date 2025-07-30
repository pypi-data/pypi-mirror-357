import click
from todo_cli.core import *

@click.group(help="A powerful CLI Todo App with search, tagging, priority, and due date support")
def main():
    pass

@main.command(help="Add a new todo task")
@click.argument('task')
@click.option('--priority', default='low', help='Task priority: low, medium, high')
@click.option('--tag', default=None, help='Optional tag to group tasks')
@click.option('--due', default=None, help='Due date in YYYY-MM-DD format')
def add(task, priority, tag, due):
    add_todo(task, priority, tag, due)

@main.command(help="List all todos with optional filters")
@click.option('--filter', type=click.Choice(['all', 'done', 'pending']), default='all', help='Filter by status')
@click.option('--tag', default=None, help='Filter by tag')
@click.option('--search', default=None, help='Search keyword in tasks')
def list(filter, tag, search):
    list_todos(filter, tag, search)

@main.command(help="Mark a todo task as done")
@click.argument('index', type=int)
def done(index):
    mark_done(index)

@main.command(help="Delete a todo task by its index")
@click.argument('index', type=int)
def delete(index):
    delete_todo(index)

@main.command(help="Edit a todo task by index")
@click.argument('index', type=int)
@click.argument('task')
def edit(index, task):
    edit_todo(index, task)
