# Sublime QuickSearchEnhanced plugin

Api for other plugins to use sublime's quick_search in bit better way.


### Installation

This plugin is part of [sublime-enhanced](http://github.com/shagabutdinov/sublime-enhanced)
plugin set. You can install sublime-enhanced and this plugin will be installed
automatically.

If you would like to install this package separately check "Installing packages
separately" section of [sublime-enhanced](http://github.com/shagabutdinov/sublime-enhanced)
package.


### Dependencies

None


### API

There are two usable classes in module:

- QuickSearches - container for opened panels; this class is preinstanciated
under "panels" variable.

- QuickSearch - quick search panel

Quick search panel are create through "create" function. Panels are stackable
(new panel hides previos when showed, and shows previous when closed).

Note that inproper code that runned in callbacks can crash sublime (due to its
internal bugs). So use this plugin with care.


##### QuickSearches.create(values = [], open = None, close = None, preview = None, text = '', callers = [], on_create = None, index = 0)

Creates a quick search panel.

Arguments:

- values - list of values in following format:

  - [string, string, ...] - list of strings.

  - [[value, line1, line2, ...], [value, line1, line2, ...]] - list of lists;
  value - any value; line1, line2, lineN - strings; note that count of lines
  always should be the same otherwise unexpected behavior of sublime are
  expected.

- open(QuickSearch) - open callback; callback called when user hits enter in
list; callback receive QuickSearch instance as argument.

- close(QuickSearch) - close callback; callback called when user hit "escape" or
"enter" (panel is closed).

- preview(QuickSearch) - preview callback; callback called when user selects an
item in list.

- text - initial text that is entered in panel.

- callers - list of callers to obtain panel instance when issuing commands over
panel in following format: [[name, object], ...] where name is name of caller
and object - instance of caller; this is usefull when you need to check that
search panel contains specific information or issues command on instance that
has opened the panel

- index - initial selected index

Result:

QuickSearch; created panel; note that panel have to be showed after it will be
created by issuing .show() command;

Example:

```
  from QuickSearchEnhanced import quick_search
  panel = quick_search.panels.create(
    ['a', 'b', 'c'],
    lambda panel: print(panel.get_current_value())
  )
```

##### QuickSearches.close_all()

Closes all panels.


##### QuickSearches.remove(panel)

Removes given panel from stack.

Arguments:

  - panel - QuickSearch; panel to remove


##### QuickSearches.get_current()

Returns currently opened panel (QuickSearch)


##### QuickSearch.show()

Shows panel. Note that it'll hide currently opened panel.


##### QuickSearch.get_values()

Get all values that are in search panel.


##### QuickSearch.set_values(values)

Set new values to panel.


##### QuickSearch.set_text(text)

Set new text to panel.


##### QuickSearch.get_callers()

Get all callers of search panel. See "callers" argument in QuickSearches.create()
above for information. Returns list of callers.


##### QuickSearch.get_caller(name)

Returns caller that has specified name. If no caller found returns None.


##### QuickSearch.get_current_index()

Returns currently selected index.


##### QuickSearch.get_current_value()

Returns currenly selected value. If no value selected returns None.


##### QuickSearch.get_current_description()

Returns list currently selected desciptions (lines).


##### QuickSearch.get_current_text()

Returns current text.


##### QuickSearch.get_panel()

Returns underlying view of opened panel.


##### QuickSearch.get_opener()

Returns view that was focused when panel was showed.


##### QuickSearch.is_visible()

Tells whether panel is visible or not.


##### QuickSearch.close(index = -1, call = True)

Closes the panel. Panel will be removed from current panels stack.

Arguments:

  index - integer; index of value; if index == -1 than last selected index will
  be used.

  call - boolean; if True then open callback will be called.


##### QuickSearch.hide()

Hide the panel. Panel can be showed later using show() method. Panel will be
not removed from panels stack.


##### QuickSearch.refresh()

Refreshes contents of panel. If one of callers responds to "refresh" method than
"refresh" method of caller that earlier in stack will be called before panel
will bee redrawed.