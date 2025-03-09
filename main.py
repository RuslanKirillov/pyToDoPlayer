from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.scrollview import ScrollView
from kivy.uix.gridlayout import GridLayout
from kivy.uix.checkbox import CheckBox
from kivy.core.window import Window
from kivy.uix.behaviors import ButtonBehavior
from kivy.uix.widget import Widget
from kivy.graphics import Color, Rectangle, Line
from kivy.utils import get_color_from_hex
from tinydb import TinyDB, Query
import os

# Указываем путь к файлу notes.json в папке с проектом
db_path = os.path.join(os.path.dirname(__file__), 'notes.json')
db = TinyDB(db_path)  # Файл для хранения заметок
Note = Query()

# Цветовая палитра
BACKGROUND_COLOR = get_color_from_hex("#FDF6E3")  # Светло-желтый/бежевый (как в Apple Notes)
TEXT_COLOR = get_color_from_hex("#4A4A4A")  # Темно-серый для текста
BUTTON_COLOR = get_color_from_hex("#D4A55E")  # Коричневый для кнопок
CHECKBOX_COLOR = get_color_from_hex("#8B7355")  # Коричневый для CheckBox

class StrikeThroughLabel(ButtonBehavior, Label):
    """Кастомный Label с зачеркиванием текста."""
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.strikethrough = False
        self.color = TEXT_COLOR  # Устанавливаем цвет текста
        self.bind(pos=self.update_canvas, size=self.update_canvas)

    def update_canvas(self, *args):
        """Обновляет зачеркивание при изменении текста или размера."""
        self.canvas.after.clear()
        if self.strikethrough:
            with self.canvas.after:
                Color(*CHECKBOX_COLOR)  # Цвет линии (коричневый)
                Line(points=[self.x, self.center_y, self.right, self.center_y], width=2)

    def toggle_strikethrough(self):
        """Переключает зачеркивание."""
        self.strikethrough = not self.strikethrough
        self.update_canvas()

class NotesApp(App):
    def build(self):
        # Основной макет
        self.layout = BoxLayout(orientation='vertical', padding=10, spacing=10)

        # Устанавливаем фон основного макета
        with self.layout.canvas.before:
            Color(*BACKGROUND_COLOR)
            self.background = Rectangle(pos=self.layout.pos, size=self.layout.size)
        self.layout.bind(pos=self.update_background, size=self.update_background)

        # Поле для ввода новой заметки
        self.note_input = TextInput(
            hint_text="Введите вашу заметку...",
            size_hint_y=None,
            height=100,
            multiline=True,
            background_color=(1, 1, 1, 1),  # Белый фон
            foreground_color=TEXT_COLOR,  # Цвет текста
            hint_text_color=(0.7, 0.7, 0.7, 1)  # Серый цвет подсказки
        )
        self.layout.add_widget(self.note_input)

        # Кнопка для сохранения заметки
        save_button = Button(
            text="Сохранить заметку",
            size_hint_y=None,
            height=50,
            background_color=BUTTON_COLOR,
            color=(1, 1, 1, 1)  # Белый текст на кнопке
        )
        save_button.bind(on_press=self.save_note)
        self.layout.add_widget(save_button)

        # Область для отображения сохраненных заметок
        self.notes_layout = GridLayout(cols=1, spacing=10, size_hint_y=None)
        self.notes_layout.bind(minimum_height=self.notes_layout.setter('height'))

        # ScrollView для прокрутки заметок
        scroll_view = ScrollView(size_hint=(1, 1))
        scroll_view.add_widget(self.notes_layout)
        self.layout.add_widget(scroll_view)

        # Загружаем сохраненные заметки при запуске
        self.load_notes()

        return self.layout

    def update_background(self, instance, value):
        """Обновляет фон при изменении размера окна."""
        self.background.pos = instance.pos
        self.background.size = instance.size

    def save_note(self, instance):
        """Сохраняет заметку в базу данных."""
        note_text = self.note_input.text.strip()
        if note_text:
            db.insert({'text': note_text, 'completed': False})  # Сохраняем заметку в базу данных
            self.note_input.text = ""  # Очищаем поле ввода
            self.load_notes()  # Обновляем список заметок

    def load_notes(self):
        """Загружает и отображает все заметки."""
        self.notes_layout.clear_widgets()  # Очищаем текущий список
        notes = db.all()  # Получаем все заметки из базы данных
        for note in notes:
            # Создаем горизонтальный макет для каждой заметки
            note_box = BoxLayout(orientation='horizontal', size_hint_y=None, height=40)

            # CheckBox для отметки выполнения
            checkbox = CheckBox(active=note['completed'], size_hint_x=None, width=40)
            checkbox.bind(active=lambda instance, value, n=note: self.toggle_completed(n, value))
            checkbox.color = CHECKBOX_COLOR  # Цвет CheckBox

            # Label с зачеркиванием
            label = StrikeThroughLabel(
                text=note['text'],
                size_hint_x=0.8,
                halign="left",
                valign="middle",
                text_size=(Window.width - 100, None)
            )
            if note['completed']:
                label.toggle_strikethrough()

            # Добавляем CheckBox и Label в макет заметки
            note_box.add_widget(checkbox)
            note_box.add_widget(label)

            # Добавляем заметку в общий макет
            self.notes_layout.add_widget(note_box)

    def toggle_completed(self, note, value):
        """Обновляет статус выполнения заметки."""
        db.update({'completed': value}, Note.text == note['text'])
        self.load_notes()  # Обновляем список заметок

if __name__ == "__main__":
    NotesApp().run()