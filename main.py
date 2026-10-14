from abc import ABC, abstractmethod
from datetime import datetime
import flet as ft

COLORS = getattr(ft, "Colors", None) or getattr(ft, "colors")
OptionCls = getattr(ft, "DropdownOption", None) or ft.dropdown.Option


class MyMap:

    def __init__(self):
        self._items = []          

    def set(self, key, value):
        for i, (k, _) in enumerate(self._items):
            if k == key:
                self._items[i] = (key, value)
                return
        self._items.append((key, value))

    def get(self, key):
        for k, v in self._items:
            if k == key:
                return v
        return None

    def values(self):  return [v for _, v in self._items]

    def __len__(self):         return len(self._items)
    def __contains__(self, k): return any(x == k for x, _ in self._items)
    def __iter__(self):        return iter(v for _, v in self._items)
    def __getitem__(self, k):
        v = self.get(k)
        if v is None:
            raise KeyError(k)
        return v
    def __eq__(self, o):   return isinstance(o, MyMap) and self._items == o._items
    def __repr__(self):    return f"MyMap({self._items!r})"
    def __str__(self):     return str(self._items)


class Entity(ABC):
    @abstractmethod
    def validate(self): ...
    @abstractmethod
    def describe(self): ...
    @abstractmethod
    def to_report(self): ...


class User(Entity):
    def __init__(self, login, password, role):
        self._login = login
        self._password = password
        self._role = role
        self._time_in = None
        self._time_out = None

    @property
    def login(self): return self._login
    @login.setter
    def login(self, v):
        if not v or len(v) < 3:
            raise ValueError("Логин >= 3 символов")
        self._login = v

    @property
    def password(self): return self._password
    @password.setter
    def password(self, v):
        if not v:
            raise ValueError("Пустой пароль")
        self._password = v

    @property
    def role(self): return self._role
    @role.setter
    def role(self, v): self._role = v

    @property
    def time_in(self): return self._time_in
    @time_in.setter
    def time_in(self, v): self._time_in = v

    @property
    def time_out(self): return self._time_out
    @time_out.setter
    def time_out(self, v): self._time_out = v

    def check_password(self, raw): return self._password == raw

    @staticmethod
    def valid_login(login):
        return bool(login) and len(login) >= 3

    def validate(self): return User.valid_login(self._login)
    def describe(self): return f"{self._login} ({self._role})"

    def to_report(self):
        ti = self._time_in.strftime(FMT) if self._time_in else "—"
        to = self._time_out.strftime(FMT) if self._time_out else "—"
        return (self._login, ti, to)

    def __eq__(self, o):
        if not isinstance(o, User): return NotImplemented
        return self._login == o._login
    def __lt__(self, o):
        if not isinstance(o, User): return NotImplemented
        return self._login < o._login
    def __le__(self, o):
        if not isinstance(o, User): return NotImplemented
        return self._login <= o._login
    def __hash__(self): return hash(self._login)
    def __len__(self):  return len(self._login)
    def __repr__(self): return f"User({self._login!r})"
    def __str__(self):  return self.describe()


class AppTitle(ft.Text):
    def __init__(self, value):
        super().__init__(value, size=22, weight=ft.FontWeight.BOLD,
                         text_align=ft.TextAlign.CENTER, color=COLORS.BLUE_700)

class LoginField(ft.TextField):
    def __init__(self, on_submit=None):
        super().__init__(label="Логин", width=280, on_submit=on_submit)

class PasswordField(ft.TextField):
    def __init__(self, on_submit=None):
        super().__init__(label="Пароль", password=True, width=280,
                         on_submit=on_submit)

class UserDropdown(ft.Dropdown):
    def __init__(self, options=None, on_change=None):
        super().__init__(label="Выбор пользователя", width=280,
                         options=options or [], on_change=on_change)

class EnterButton(ft.ElevatedButton):
    def __init__(self, on_click):
        super().__init__("Войти", width=280, on_click=on_click)

class ExitButton(ft.ElevatedButton):
    def __init__(self, on_click):
        super().__init__("Выйти", width=280, on_click=on_click, disabled=True)

class StatusText(ft.Text):
    def __init__(self):
        super().__init__("Введите логин и пароль", size=13,
                         text_align=ft.TextAlign.CENTER, color=COLORS.GREY_700)

class InfoRow(ft.Row):
    def __init__(self, text, color=COLORS.BLACK):
        super().__init__([ft.Text(text, size=13, color=color)],
                         alignment=ft.MainAxisAlignment.CENTER)

class SessionList(ft.ListView):
    def __init__(self):
        super().__init__(height=200, spacing=4, padding=8, auto_scroll=True)

class DividerLine(ft.Divider):
    def __init__(self):
        super().__init__(height=1, color=COLORS.GREY_300)

class CardBox(ft.Container):
    def __init__(self, content):
        super().__init__(content=content, width=400, padding=24,
                         border_radius=16, bgcolor=COLORS.WHITE)

class MainColumn(ft.Column):
    def __init__(self, controls):
        super().__init__(controls, spacing=10,
                         horizontal_alignment=ft.CrossAxisAlignment.CENTER)

class App(Entity):
    def __init__(self, page):
        self._page = page
        self._users = MyMap()
        self._current = None
        self._saved = False
        self._seed()
        self._build()
        self._register_close()

    def _seed(self):
        """10 пользовательских объектов в коллекции MyMap."""
        data = [
            ("admin", "admin123", "Админ"),   ("ivanov", "ivan123", "Менеджер"),
            ("petrov", "petr123", "Разработчик"), ("sidorov", "sid123", "Тестировщик"),
            ("kuznetsova", "kuz123", "Аналитик"), ("smirnov", "smir123", "Developer"),
            ("volkova", "vol123", "Дизайнер"),    ("morozov", "mor123", "Бухгалтер"),
            ("novikov", "nov123", "Программист"),          ("fedorova", "fed123", "Тимлид"),
        ]
        for login, pwd, role in data:
            self._users.set(login, User(login, pwd, role))

    def _build(self):
        page = self._page
        page.title = "Журнал входов"
        page.bgcolor = COLORS.GREY_100
        page.padding = 20
        page.horizontal_alignment = ft.CrossAxisAlignment.CENTER
        page.vertical_alignment = ft.MainAxisAlignment.CENTER

        self._dd = UserDropdown(
            options=[OptionCls(u.login) for u in self._users.values()],
            on_change=self._on_pick)
        self._login_f = LoginField(on_submit=self._do_login)
        self._pwd_f = PasswordField(on_submit=self._do_login)
        self._in_btn = EnterButton(self._do_login)
        self._out_btn = ExitButton(self._do_logout)
        self._status = StatusText()
        self._divider = DividerLine()
        self._list = SessionList()
        self._label = InfoRow("Записи:", COLORS.BLUE_700)

        col = MainColumn([
            AppTitle("Журнал входов"), self._dd, self._login_f, self._pwd_f,
            self._in_btn, self._out_btn, self._divider,
            self._status, self._label, self._list,
        ])
        page.add(ft.Row([CardBox(col)], alignment=ft.MainAxisAlignment.CENTER))
        self._refresh()

    def _on_pick(self, e):
        self._login_f.value = e.control.value or ""
        self._page.update()

    def _do_login(self, e=None):
        if self._current is not None:
            self._set_status("Сначала выйдите", COLORS.ORANGE_700)
            return
        user = self._users.get((self._login_f.value or "").strip())
        if user is None:
            self._set_status("Нет такого пользователя", COLORS.RED_700)
            return
        if not user.check_password((self._pwd_f.value or "").strip()):
            self._set_status("Неверный пароль", COLORS.RED_700)
            return
        user.time_in = datetime.now()
        user.time_out = None
        self._current = user
        self._login_f.value = self._pwd_f.value = ""
        self._in_btn.disabled, self._out_btn.disabled = True, False
        self._set_status(f"Вход: {user.describe()}", COLORS.GREEN_700)
        self._refresh()
        self._safe_update()

    def _do_logout(self, e=None):
        if self._current is None:
            return
        self._current.time_out = datetime.now()
        self._set_status(f"Выход: {self._current.login}", COLORS.BLUE_700)
        self._current = None
        self._in_btn.disabled, self._out_btn.disabled = False, True
        self._refresh()
        self._safe_update()

    def _set_status(self, text, color):
        self._status.value = text
        self._status.color = color

    def _refresh(self):
        self._list.controls.clear()
        for u in sorted(self._users.values()):   
            if u.time_in is None:
                continue
            ti = u.time_in.strftime(FMT)
            to = u.time_out.strftime(FMT) if u.time_out else "…"
            color = COLORS.GREEN_700 if u.time_out is None else COLORS.BLACK
            self._list.controls.append(InfoRow(f"{u.login}: {ti} → {to}", color))
        if not self._list.controls:
            self._list.controls.append(InfoRow("— записей нет —", COLORS.GREY_500))

    def _safe_update(self):
        try:
            self._page.update()
        except Exception:
            pass

    @staticmethod
    def build_report(users):
        cols = ("login", "time_in", "time_out")
        rows = [u.to_report() for u in users]
        widths = [len(c) for c in cols]
        for r in rows:
            for i in range(3):
                widths[i] = max(widths[i], len(r[i]))

        sep = "+" + "+".join("-" * (w + 2) for w in widths) + "+"
        def line(row):
            return "| " + " | ".join(row[i].ljust(widths[i]) for i in range(3)) + " |"

        out = [sep, line(cols), sep]
        out += [line(r) for r in rows]
        out.append(sep)
        return "\n".join(out)

    def save_report(self):
        if self._saved:
            return
        self._saved = True
        if self._current is not None:
            self._current.time_out = datetime.now()
            self._current = None
        try:
            with open(REPORT_FILE, "w", encoding="utf-8") as f:
                f.write(App.build_report(self._users.values()) + "\n")
            print("Отчёт сохранён в", REPORT_FILE)
        except Exception as ex:
            print("Ошибка отчёта:", ex)

    def _register_close(self):
        try:
            self._page.window.prevent_close = True
            self._page.window.on_close = self._on_close
        except Exception:
            pass
        try:
            self._page.on_disconnect = lambda e: self.save_report()
        except Exception:
            pass

    def _on_close(self, e):
        self.save_report()
        try:
            self._page.window.prevent_close = False
            self._page.window.destroy()
        except Exception:
            pass

    def validate(self):  return len(self._users) > 0
    def describe(self):  return f"App(users={len(self._users)})"
    def to_report(self): return App.build_report(self._users.values())

    def __eq__(self, o):  return isinstance(o, App) and self._users == o._users
    def __lt__(self, o):
        if not isinstance(o, App): return NotImplemented
        return len(self) < len(o)
    def __len__(self):    return len(self._users)
    def __hash__(self):   return hash(len(self))
    def __repr__(self):   return self.describe()
    def __str__(self):    return "Журнал входов"


def main(page: ft.Page):
    App(page)


if __name__ == "__main__":
    (getattr(ft, "run", None) or getattr(ft, "app"))(main)
