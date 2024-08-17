import flet as ft
import sqlite3

class ToDo:
    def __init__(self, Page: ft.Page):
        """
        Initializes a new instance of the ToDo class with the specified Page.

        Args:
            Page (ft.Page): The Page to be used for the ToDo instance.

        Returns:
            None
        """
        self.Page = Page
        self.Page.bgcolor = ft.colors.WHITE
        self.Page.window.width = 350
        self.Page.window.height = 450
        self.Page.window.resizable = False
        self.Page.window.always_on_top = True
        self.Page.title = "To-Do App"
        self.task = ''
        self.view = 'all'
        self.db_execute('CREATE TABLE IF NOT EXISTS tasks (name, status)')
        self.results = self.db_execute('SELECT * FROM tasks')        
        self.main_Page()

    def checked(self, e):
        """
        Updates the task status in the database based on the checkbox event.

        Parameters:
            e (Event): The event triggered by the checkbox.

        Returns:
            None
        """
        is_checked = e.control.value
        label = e.control.label
        
        if is_checked:
            self.db_execute('UPDATE tasks SET status = ? WHERE name = ?',  params=["complete", label])
        else:
            self.db_execute('UPDATE tasks SET status = ? WHERE name = ?', params=["incomplete", label])

        if self.view == 'all':
            self.results = self.db_execute('SELECT * FROM tasks')
        else:
            self.results = self.db_execute('SELECT * FROM tasks WHERE status = ?', params=[self.view])
            
        self.update_task_list()
        self.Page.update()
    
    def tasks_container(self):
        """
        Returns a container for tasks with a height of 80% of the Page height.
        
        The container includes a column with a checkbox control labeled "Tarefa 1" 
        that is initially checked.
        
        Parameters:
            self (ToDo): The instance of the ToDo class.
        
        Returns:
            ft.Container: A container with the specified height and content.
        """
        return ft.Container(
            height=self.Page.height * 0.8,
            content = ft.Column(
                controls = [
                    ft.Checkbox(
                        label = res[0],
                        on_change = self.checked, 
                        value = True if res[1] == 'complete' else False
                        )
                    for res in self.results if res                    
                ]
            )
        )

    def db_execute(self, query, params = []):
        """
        Execute a SQL query on the todo.db database.

        Parameters:
            query (str): The SQL query to be executed.
            params (list): A list of parameters to be used in the query.

        Returns:
            list: A list of rows returned by the query.
        """
        with sqlite3.connect(r'D:\Projetos-Fernando\Python\ToDoApp\Database\todo.db') as conn:
            cur = conn.cursor()
            cur.execute(query, params)
            conn.commit()
            return cur.fetchall()
    
    def set_value(self, e):
        """
        Sets the task value based on the event triggered by the control.

        Parameters:
            e (Event): The event triggered by the control.

        Returns:
            None
        """
        self.task = e.control.value

    def update_task_list(self):
        """
        Updates the task list in the application.

        Parameters:
            self (ToDo): The instance of the ToDo class.

        Returns:
            None
        """
        tasks = self.tasks_container()
        self.Page.controls.pop()
        self.Page.add(tasks)
        self.Page.update()
        
    def add_task(self, e, input_task):
        """
        Adds a new task to the task list.

        Parameters:
            e (Event): The event triggered by the control.
            input_task (Control): The input task control.

        Returns:
            None
        """
        task_name = self.task
        status = 'incomplete'
        
        if task_name:
            self.db_execute(
                query='INSERT INTO tasks VALUES (?, ?)',
                params=(task_name, status)
                )
            input_task.value = ''
            self.results = self.db_execute('SELECT * FROM tasks')
            self.update_task_list()
    
    def tabs_changed(self, e):
        """
        Updates the task list based on the selected tab.

        Parameters:
            e (Event): The event triggered by the control.

        Returns:
            None
        """
        if e.control.selected_index == 0:
            self.results = self.db_execute('SELECT * FROM tasks')
            self.view = 'all'
        elif e.control.selected_index == 1:
            self.results = self.db_execute('SELECT * FROM tasks WHERE status = ?', params=['incomplete'])
            self.view = 'incomplete'
        elif e.control.selected_index == 2:
            self.results = self.db_execute('SELECT * FROM tasks WHERE status = ?', params=['complete'])
            self.view = 'complete'
        
        self.update_task_list()
    
    def main_Page(self):
        """
        Initializes the main Page of the application.

        This function sets up the main Page of the application by creating and adding the necessary components.

        Parameters:
            self (ToDo): The instance of the ToDo class.

        Returns:
            None
        """
        input_task = ft.TextField(
            hint_text = "Digite aqui uma tarefa", 
            expand = True,
            on_change = self.set_value
            )
        input_bar = ft.Row(
            controls = [input_task,
                        ft.FloatingActionButton(
                            icon = ft.icons.ADD, 
                                on_click = lambda e: self.add_task(e, input_task)
                                )
                        ]
        )
        
        tabs = ft.Tabs(
            selected_index = 0,
            on_change = self.tabs_changed,
            tabs = [
                ft.Tab(text = "Todos"),
                ft.Tab(text = "Em andamento"),
                ft.Tab(text = "Finalizados")
            ]
        )
        
        tasks = self.tasks_container()
        
        self.Page.add(input_bar, tabs, tasks)
        
ft.app(target=ToDo)