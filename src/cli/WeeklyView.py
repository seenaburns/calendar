import curses
from ListView import *
from TimeView import *

class WeeklyView(TimeView,ListView):
  def __init__(self, EventStore):
    # super init intializes in reverse order of multiple inheritance seemingly
    # e.g. Class(C1, C2) is init'ed in C2, C1 order
    super(WeeklyView, self).__init__()

    self.event_lists = []
    for i in range(7):
      self.event_lists.append([])

    self.EventStore = EventStore

    self.box_header_width = 11

    self.get_period_func = self.get_week_period
    self.offset_period_func = self.apply_week_offset

  def draw_box_header(self,y,index):
    headers = ['Sunday', 'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday']
    self.pad.addstr(y,2,headers[index].ljust(self.box_header_width))

  def update(self):
    self.clear_events()
    self.EventStore.add_filter('date', self.period)
    self.add_events(self.EventStore.get_events())
    super(WeeklyView, self).update()

  def clear_events(self):
    for i in range(len(self.event_lists)):
      self.event_lists[i] = []

  def add_events(self,events):
    for e in events:
      index = (e.startDate.weekday() + 1)%7
      self.add_event(index, e)