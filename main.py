import json
import matplotlib
import numexpr as ne
import numpy as np

from functools import partial
from tkinter import *
from tkinter.filedialog import asksaveasfile, asksaveasfile, askopenfile

from matplotlib import pyplot as plt

from matplotlib.backends.backend_tkagg import (FigureCanvasTkAgg,
                                               NavigationToolbar2Tk)
matplotlib.use('TkAgg')
class Entries:
    def __init__(self):
        self.entries_list = []
        self.parent_window = None
    def set_parent_window(self, parent_window):
        self.parent_window = parent_window

    def add_entry(self, func=""):
        new_entry = Entry(self.parent_window)
        new_entry.insert(0, func)
        new_entry.icursor(0)
        new_entry.focus()
        new_entry.pack()
        plot_button = self.parent_window.get_button_by_name('plot')
        if plot_button:
            plot_button.pack_forget()
        self.parent_window.add_button('plot', 'Plot', 'plot', hot_key='<Return>')
        self.entries_list.append(new_entry)

    def delete_text_line(self):
       if len(self.entries_list) == 0:
            wn = ModalWindow(self.parent_window, title='Нет существующих полей', labeltext='Нет полей, которые можно удалить')
            but = Button(master=wn.top, text='Ok', command=wn.cancel )
            wn.add_button(but)
       focus = self.parent_window.focus_get()
       if type(focus) == Entry:
                if focus.get() != "":
                    check_win = ModalWindow(self.parent_window, title='Удалить поле для ввода функции', labeltext='У вас непустое поле. Вы уверены, что хотите продолжить?')
                    command = partial(check_win.continue_to_delete_text_line, entry=focus, entries_list=self.entries_list)
                    yes = Button(master=check_win.top, text='Продолжить', command=command)
                    check_win.add_button(yes)
                    no = Button(master=check_win.top, text="Отмена", command=check_win.cancel)
                    check_win.add_button(no)
                else:
                    self.entries_list.pop(self.entries_list.index(focus)).destroy()
                plot_but = self.parent_window.get_button_by_name('plot')
                if plot_but:
                    plot_but.pack_forget()
                self.parent_window.add_button('plot', 'Plot', 'plot', hot_key='<Return>')


class Plotter:
    def __init__(self, x_min=-20, x_max=20, dx=0.01):
        self.x_min = x_min
        self.x_max = x_max
        self.dx = dx
        self._last_plotted_list_of_function = None
        self._last_plotted_figure = None
        self.parent_window = None
    def set_parent_window(self, parent_window):
        self.parent_window = parent_window
    # plotting of graphics (построение графиков функций)
    def plot(self, list_of_function, title='Графики функций', x_label='x', y_label='y', need_legend=True):
        fig = plt.figure()
        x = np.arange(self.x_min, self.x_max, self.dx)
        new_funcs = [f if 'x' in f else 'x/x * ({})'.format(f) for f in list_of_function]
        ax = fig.add_subplot(1, 1, 1)
        for func in new_funcs:
            ax.plot(x, ne.evaluate(func), linewidth=1.5)
        fig.suptitle(title)
        plt.xlabel(x_label)
        plt.ylabel(y_label)
        if need_legend:
            plt.legend(list_of_function)
        self._last_plotted_list_of_function = list_of_function
        self._last_plotted_figure = fig
        return fig
class Commands:
    class State:
        def __init__(self):
            self.list_of_function = []
        def save_state(self):
            tmp_dict = {'list_of_function': self.list_of_function}
            file_out = asksaveasfile(defaultextension=".json")
            if file_out is not None:
                json.dump(tmp_dict, file_out)
            return self
        def reset_state(self):
            self.list_of_function = []
    def __init__(self):
        self.command_dict = {}
        self.__figure_canvas = None
        self.__navigation_toolbar = None
        self._state = Commands.State()
        self.__empty_entry_counter = 0
        self.parent_window = None
    def set_parent_window(self, parent_window):
        self.parent_window = parent_window
    def add_command(self, name, command):
        self.command_dict[name] = command
    def get_command_by_name(self, command_name):
        return self.command_dict[command_name]
    def __forget_canvas(self):
        if self.__figure_canvas is not None:
            self.__figure_canvas.get_tk_widget().pack_forget()
    def __forget_navigation(self):
        if self.__navigation_toolbar is not None:
            self.__navigation_toolbar.pack_forget()
    def plot(self, *args, **kwargs):
        def is_not_blank(s):
            return bool(s and not s.isspace())
        self._state.reset_state()
        list_of_function = []
        for entry in self.parent_window.entries.entries_list:
            get_func_str = entry.get()
            self._state.list_of_function.append(get_func_str)
            if is_not_blank(get_func_str):
                list_of_function.append(get_func_str)
            else:
                if self.__empty_entry_counter == 0:
                    mw = ModalWindow(self.parent_window, title='Пустая строка', labeltext='Это пример модального окна, '
                                                                                          'возникающий, если ты ввел '
                                                                                          'пустую '
                                                                                          'строку. С этим ничего '
                                                                                          'делать не нужно. '
                                                                                          'Просто нажми OK :)')
                    ok_button = Button(master=mw.top, text='OK', command=mw.cancel)
                    mw.add_button(ok_button)
                    self.__empty_entry_counter = 1
        self.__empty_entry_counter = 0
        figure = self.parent_window.plotter.plot(list_of_function)
        self._state.figure = figure
        self.__forget_canvas()
        self.__figure_canvas = FigureCanvasTkAgg(figure, self.parent_window)
        self.__forget_navigation()
        self.__navigation_toolbar = NavigationToolbar2Tk(self.__figure_canvas, self.parent_window)
        self.__figure_canvas.get_tk_widget().pack(side=TOP, fill=BOTH, expand=1)
        plot_button = self.parent_window.get_button_by_name('plot')
        if plot_button:
            plot_button.pack_forget()
    def add_func(self, *args, **kwargs):
        self.__forget_canvas()
        self.__forget_navigation()
        self.parent_window.entries.add_entry()
    def save_as(self):
        self._state.save_state()
        return self

    def open_file(self):
        self.__forget_canvas()
        file = askopenfile(filetypes=[("function objects", ".json")])
        if file is not None:
            for entry in self.parent_window.entries.entries_list:
                entry.destroy()
            self.parent_window.entries.entries_list = []
            func_from_file = json.load(file)
            for func in func_from_file['list_of_function']:
                self.parent_window.entries.add_entry(func)
            self.parent_window.commands.plot()

    def delete_text_line(self, *args, **kwargs):
        self.__forget_canvas()
        self.__forget_navigation()
        self.parent_window.entries.delete_text_line()


class Buttons:
    def __init__(self):
        self.buttons = {}
        self.parent_window = None
    def set_parent_window(self, parent_window):
        self.parent_window = parent_window
    def add_button(self, name, text, command):
        new_button = Button(master=self.parent_window, text=text, command=command)
        self.buttons[name] = new_button
        return new_button
    def delete_button(self, name):
        button = self.buttons.get(name)
        if button:
            button.pack_forget()

class ModalWindow:
    def __init__(self, parent, title, labeltext=''):
        self.buttons = []
        self.top = Toplevel(parent)
        self.top.transient(parent)
        self.top.grab_set()
        if len(title) > 0:
            self.top.title(title)
        if len(labeltext) == 0:
            labeltext = 'Default text'
        Label(self.top, text=labeltext).pack()
    def add_button(self, button):
        self.buttons.append(button)
        button.pack(pady=5)
    def cancel(self):
        self.top.destroy()

    def continue_to_delete_text_line(self, entry, entries_list):
        entry.delete(0, END)
        self.top.destroy()
        entries_list.pop(entries_list.index(entry)).destroy()


# app class (класс приложения)
class App(Tk):
    def __init__(self, buttons, plotter, commands, entries):
        super().__init__()
        self.buttons = buttons
        self.plotter = plotter
        self.commands = commands
        self.entries = entries
        self.entries.set_parent_window(self)
        self.plotter.set_parent_window(self)
        self.commands.set_parent_window(self)
        self.buttons.set_parent_window(self)
    def add_button(self, name, text, command_name, *args, **kwargs):
        hot_key = kwargs.get('hot_key')
        if hot_key:
            kwargs.pop('hot_key')
        callback = partial(self.commands.get_command_by_name(command_name), *args, **kwargs)
        new_button = self.buttons.add_button(name=name, text=text, command=callback)
        if hot_key:
            self.bind(hot_key, callback)
        new_button.pack(fill=BOTH)
    def get_button_by_name(self, name):
        return self.buttons.buttons.get(name)
    def create_menu(self):
        menu = Menu(self)
        self.config(menu=menu)

        file_menu = Menu(menu)
        file_menu.add_command(label="Save as...", command=self.commands.get_command_by_name('save_as'))
        file_menu.add_command(label="Open file...", command=self.commands.get_command_by_name('open_file'))
        menu.add_cascade(label="File", menu=file_menu)


if __name__ == "__main__":
    # init buttons (создаем кнопки)
    buttons_main = Buttons()
    # init plotter (создаем отрисовщик графиков)
    plotter_main = Plotter()
    # init commands for executing on buttons or hot keys press
    # (создаем команды, которые выполняются при нажатии кнопок или горячих клавиш)
    commands_main = Commands()
    # init entries (создаем текстовые поля)
    entries_main = Entries()
    # command's registration (регистрация команд)
    commands_main.add_command('plot', commands_main.plot)
    commands_main.add_command('add_func', commands_main.add_func)
    commands_main.add_command('save_as', commands_main.save_as)
    commands_main.add_command('open_file', commands_main.open_file)
    commands_main.add_command('delete_text_line', commands_main.delete_text_line)
    # init app (создаем экземпляр приложения)
    app = App(buttons_main, plotter_main, commands_main, entries_main)
    # init add func button (добавляем кнопку добавления новой функции)
    app.add_button('add_func', 'Добавить функцию', 'add_func', hot_key='<Control-a>')
    app.add_button('add_func', 'Добавить поле ', 'add_func', hot_key='<Control-n>')
    app.add_button('delete_text_line', 'Удалить поле ', 'delete_text_line', hot_key='<Alt-F4>')
    # init first entry (создаем первое поле ввода)
    entries_main.add_entry()
    app.create_menu()
    # добавил комментарий для коммита
    # application launch (запуск "вечного" цикла приложеня)
    app.mainloop()