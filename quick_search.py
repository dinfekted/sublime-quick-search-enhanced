import sublime
import sublime_plugin
import re

setattr(sublime, 'panels', [])

class QuickSearchCloseContainer():
  def __init__(self, panels, close):
    self.panel = None
    self.panels = panels
    self.close = close

  def complete(self, result):
    self.panels.remove(self.panel)
    if self.close != None:
      self.close(result)
    current = self.panels.get_current()
    if current != None:
      current.refresh()
      current.show()

class QuickSearches():

  def __init__(self):
    sublime.panels = []

  def get_current(self):
    if len(sublime.panels) == 0:
      return None

    return sublime.panels[-1]

  def create(self, values = [], open = None, close = None, preview = None,
    text = '', callers = [], on_create = None, index = 0):

    current = self.get_current()
    if current != None and current.is_visible():
      current.hide()

    container = QuickSearchCloseContainer(self, close)
    panel = QuickSearch(values, open, preview, container.complete, text,
      callers, on_create, index)

    container.panel = panel
    sublime.panels.append(panel)
    return panel

  def remove(self, panel):
    sublime.panels.remove(panel)

  def close_all(self):
    for panel in reversed(self.panels):
      panel.close()

panels = QuickSearches()

class QuickSearch():

  def __init__(self, values = [], open = None, preview = None, close = None,
    text = '', callers = [], on_create = None, index = 0):

    self.window = sublime.active_window()
    self.waiting = False
    self.closing = False
    self.refreshing = False

    self.panel = None
    self.current = index or 0
    self.visible = False
    self.opener = None

    self.callers = callers
    self.text = text or ''
    self.values = values
    self.open = open

    self._on_close = close
    self.preview = preview
    self.on_create = on_create

  # def get_current():
  #   return sublime.active_window().getattr('__search_panel', None)

  def show(self):
    sublime.set_timeout(self._show, 10)

  def _show(self):
    if self.is_visible() or len(self.values) == 0:
      return

    values = []
    for value in self.values:
      if isinstance(value, list):
        values.append(value[1:])
      else:
        values.append(value)

    if self.opener == None:
      self.opener = self.window.active_view()

    self.waiting = True
    self.window.show_quick_panel(values, self._complete, 0, self.current or 0,
      self._preview)

  def _none(self, a):
    return

  def get_values(self):
    return self.values

  def set_values(self, values):
    self.values = values
    self.refresh()

  def set_text(self, text):
    self.text = text
    self.refresh()

  def get_callers(self):
    return self.callers

  def get_caller(self, name):
    for caller in self.callers:
      if caller[0] == name:
        return caller[1]

    return None

  def get_current_index(self):
    return self.current

  def get_current_value(self):
    if self.current == None or self.current < 0:
      return None

    value = self.values[self.current]
    if isinstance(value, list):
      return value[0]
    else:
      return value

  def get_current_description(self):
    if self.current == None:
      return None

    value = self.values[self.current]
    if isinstance(value, list):
      return value[1:]
    else:
      return [value]

  def get_current_text(self):
    if self.panel == None:
      return self.text

    return self.panel.substr(sublime.Region(0, self.panel.size()))

  def get_panel(self):
    return self.panel

  def get_opener(self):
    return self.opener

  def is_visible(self):
    return self.panel != None

  def close(self, index = -1, call = True):
    if self.closing:
      return

    self.closing = True
    self.hide()
    if self.open != None:
      if index != -1:
        self.current = index
      if call:
        self.open(self)

    if self._on_close != None:
      self._on_close(self)

    self.closing = False

  def hide(self):
    if self.text == None:
      self.text = self.get_current_text()

    if self.is_visible():
      self.panel = None
      self.window.run_command("hide_overlay")

  def refresh(self):
    if self.refreshing:
      return

    self.refreshing = True
    for caller in self.callers:
      if 'refresh' in dir(caller[1]):
        caller[1].refresh()
        break

    self.refreshing = False
    if not self.is_visible():
      return

    self.hide()
    self.show()

  def _complete(self, index):
    if self.closing or not self.is_visible():
      return

    if index == -1:
      index = None

    self.current = index
    self.panel = None
    self.text = self.get_current_text()
    self.close()

  def _preview(self, index):
    self.current = index
    if self.preview == None:
      return

    if self.is_visible():
      self.preview(self)

  def _on_show(self, view):
    self.panel = view

    if self.text == None or self.text == '':
      self.current = 0
      if self.preview != None:
        self.preview(self)
      self.text = None
    else:
      self.panel.run_command('insert', {'characters': self.text})

    self.text = None
    self.waiting = False
    if self.on_create != None:
      self.on_create(self)

class Listener(sublime_plugin.EventListener):

  def on_activated(self, view):
    panel = panels.get_current()
    if(panel == None or panel.is_visible() or not panel.waiting or
      view.file_name() != None):
      return

    panel._on_show(view)

class Context(sublime_plugin.EventListener):
  def on_query_context(self, view, key, operator, operand, match_all):
    panel = panels.get_current()
    if key != 'search_panel_name' or panel == None or not panel.is_visible():
      return None

    callers = [['search_panel', None]] + panel.get_callers()
    names = []
    for caller in callers:
      names.append(caller[0])

    name = ' '.join(names)

    if operator == sublime.OP_EQUAL:
      return name == operand
    elif operator == sublime.OP_NOT_EQUAL:
      return name != operand
    elif operator == sublime.OP_REGEX_MATCH:
      return re.match(operand, name) != None
    elif operator == sublime.OP_NOT_REGEX_MATCH:
      return re.match(operand, name) == None
    elif operator == sublime.OP_REGEX_CONTAINS:
      return re.search(operand, name) != None
    elif operator == sublime.OP_NOT_REGEX_CONTAINS:
      return re.search(operand, name) == None

    raise Exception('Unsupported operator: ' +str(operator))