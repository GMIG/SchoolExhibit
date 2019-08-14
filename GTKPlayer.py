from twisted.internet import gtk3reactor
gtk3reactor.install()

from gi.repository import Gtk
app = Gtk.Application(...)

from twisted import reactor
reactor.registerGApplication(app)
reactor.run()
