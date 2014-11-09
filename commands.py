import sublime
import sublime_plugin

from QuickSearchEnhanced import quick_search

class ExpandPanelValue(sublime_plugin.TextCommand):
  def run(self, edit):
    panel = quick_search.panels.get_current()
    title = panel.get_current_description()

    if title == None:
      return

    panel.set_text(title[0])