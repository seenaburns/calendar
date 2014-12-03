import sys
import curses
import traceback
import time
import signal
import random

from ListView import *
from DailyView import *
from SummaryView import *
from CommandView import *
from event import *
from eventstore import *

global resize_flag
def handle_sigwinch(signum, frame):
  global resize_flag
  resize_flag = True

signal.signal(signal.SIGWINCH, handle_sigwinch)

class NcursesDisplay:
  def __init__(self):
    pass

  def setup_curses(self):
    # main window, stdscr
    self.stdscr = curses.initscr()
    # self.stdscr.nodelay(1)
    curses.halfdelay(1)
    self.stdscr.refresh()

    # Height, width of terminal window
    self.h, self.w = self.stdscr.getmaxyx()

    # Ncurses settings
    curses.noecho()
    curses.cbreak()
    # Disable cursor if possible
    if curses.tigetstr("cnorm"):
      curses.curs_set(0)

    global resize_flag
    resize_flag = False

  def cleanup_curses(self):
    # End curses session to prevent window from breaking on error
    curses.nocbreak()
    curses.echo()
    curses.endwin()

  def display(self):
    try:
      self.setup_curses()

      es = EventStore()
      self.DailyView = DailyView(es)
      self.SummaryView = SummaryView()
      self.CommandView = CommandView()
      self.resize_views()

      self.DailyView.display()
      self.SummaryView.display()
      self.CommandView.display()

      global resize_flag

      while True:
        self.DailyView.display()
        self.SummaryView.display()
        self.CommandView.display()
        # curses.doupdate()
        
        c = self.stdscr.getch()

        if c == curses.KEY_RESIZE or resize_flag:
          self.cleanup_curses()
          self.setup_curses()
          self.resize_views()

        if c == ord('q'):
          # Exit
          break
        # WASD Scrolling
        elif c == ord('a'):
          self.DailyView.scroll_x(-1)
        elif c == ord('d'):
          self.DailyView.scroll_x(1)
        elif c == ord('s'):
          self.DailyView.scroll_y(1)
        elif c == ord('w'):
          self.DailyView.scroll_y(-1)
        elif c == ord('r'):
          self.DailyView.add_event(random.randint(0,19), Event())

        # time.sleep(0.01)

      self.cleanup_curses()
    except Exception as e:
      # Safely exit on exception rather than damage terminal text rendering
      self.cleanup_curses()
      print(e)
      traceback.print_exc()
      sys.exit(1)

  def resize_views(self):
      self.DailyView.set_view_position(0,0)
      self.DailyView.set_view_size(self.w-1,self.h*2/3-1)
      self.DailyView.set_content_size(self.w,self.h)

      self.SummaryView.set_view_position(0,self.DailyView.view_h+1)
      self.SummaryView.set_view_size(self.w-1,self.h-self.DailyView.view_h-3)
      self.SummaryView.set_content_size(self.w,(self.h-1)*2/3)

      self.CommandView.set_view_position(0,self.h-1)
      self.CommandView.set_view_size(self.w-1,1)
      self.CommandView.set_content_size(self.w,1)