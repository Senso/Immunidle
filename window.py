import urwid

class MainWindow:
    ##(name, foreground, background, mono, foreground_high, background_high)
    palette = [
        ('body', '', '', '', '#fff', '#000'),
        ('footer', '', '', '', '#fff', '#000'),
        ('header', '', '', '', '#fff', '#000'),
        ('white', '', '', '', '#fff', '#000'),
        ('brown', '', '', '', '#d80', '#000'),
        ('yellow', '', '', '', '#ff0', '#000'),
        ('red', '', '', '', '#f00', '#000'),
        ('flash brown', '', '', 'bold', '#d80,standout', '#000'),
        ('flash yellow', '', '', 'bold', '#ff0,standout', '#000'),
        ('flash red', '', '', 'bold', '#f00,standout', '#000'),
        ('light white', '', '', 'bold', '#fff', '#000'),
        ('light blue', '', '', 'bold', '#0af', '#000'),
        ('white blue', '', '', '', '#adf', '#000'),
    ]

    def __init__(self, game):
        self.game = game

        self.game.initialize_player()

        self.header_text = urwid.Text(u"Top\nheader")
        self.header = urwid.AttrWrap(self.header_text, 'header')

        # self.cell_txt = urwid.Text("")
        # self.antigen_txt = urwid.Text("")
        # self.player_col = urwid.Filler(self.cell_txt, valign='top', height='pack')
        # self.antigen_col = urwid.Filler(self.antigen_txt, valign='top', height='pack')
        # self.body = urwid.Columns([urwid.LineBox(self.player_col), urwid.LineBox(self.antigen_col)])

        self.area = GameArea()

        self.footer_text = urwid.Text(u"")
        self.footer = urwid.AttrWrap(self.footer_text, 'footer')

        self.view = MainFrame(header=self.header, body=self.area.body, footer=self.footer, focus_part='body')
        self.view.mainloop = self

        self.last_alarm = None

    def main(self):

        #self.loop = urwid.MainLoop(self.view, self.palette, input_filter=self.input_filter) #, pop_ups=True)
        self.loop = urwid.MainLoop(self.view, self.palette, pop_ups=True)
        #self.loop.mwin = self

        self.loop.screen.set_terminal_properties(colors=256)
        self.loop.screen.register_palette(self.palette)

        ### TODO: check that constantly adding alerts doesn't leak mem

        # 1-second game tick
        self.last_alarm = self.loop.set_alarm_in(0, callback=self.game_tick)
        # 10-second game tick
        #self.loop.set_alarm_in(0, callback=self.protein_gain)

        self.loop.run()

    def write_header(self):
        header_txt = "Ticks: %s\nProteins: %s\nLevel: %s\n" % (self.game.ticks, self.game.proteins, self.game.level)
        self.header_text.set_text(header_txt)

    def write_footer(self):
        footer_txt = self.game.display_log()
        self.footer_text.set_text(footer_txt)

    def draw_cells(self):
        cell_str = []
        for i in self.game.player_cells:
            cell_str.append((i.palette, i.symbol))
        if cell_str:
            self.area.cells.set_text(cell_str)

    def draw_antigens(self):
        antigen_str = []
        for i in self.game.antigens:
            antigen_str.append((i.palette, i.symbol))
        if antigen_str:
            self.area.antigens.set_text(antigen_str)    

    def game_tick(self, loop, user_data):
        # So we have a single alarm object at all times?
        self.loop.remove_alarm(self.last_alarm)

        self.write_header()

        self.draw_cells()
        self.draw_antigens()

        self.write_footer()

        # If the game is paused, skip these events
        if not self.game.paused:
            # Player attacks
            self.game.player_attack(self)

            # Gain a protein
            self.protein_gain(1)

            self.game.check_level_state()
            self.game.age_all_cells()
            self.game.ticks += 1

        self.last_alarm = self.loop.set_alarm_in(sec=1, callback=self.game_tick)

    def protein_gain(self, amount=0):
        self.game.proteins += amount

class MainFrame(urwid.Frame):

    def keypress(self, size, key):
        #self.mainloop.game.log("key pressed: %s" % key)
        if key == 'q':
            raise urwid.ExitMainLoop()
        elif key == 'n':
            self.mainloop.game.spawn_cell()
            self.mainloop.write_header()
        elif key == 'd':
            self.purchase_pop_up()
        elif key == ' ':
            if self.mainloop.game.paused:
                self.mainloop.game.log("Game unpaused.")
                self.mainloop.game.paused = False
            else:
                self.mainloop.game.log("Game paused.")
                self.mainloop.game.paused = True

    def purchase_pop_up(self):

        question = urwid.Text(("bold", "A pop-up!"), "center")
        prompt = urwid.LineBox(urwid.Filler(question))
        overlay = OptionOverlay(
            top_w = prompt, 
            bottom_w = self,
            align = 'left',
            width = 10,
            valign = 'middle',
            height = 6,
            left = 5,
            )
        self.mainloop.loop.widget = overlay


class OptionOverlay(urwid.Overlay):
    def selectable(self):
        return True

    def keypress(self, size, key):
        if key == 'q':
            raise urwid.ExitMainLoop()
        elif key == 'enter':
            self.bottom_w.mainloop.loop.widget = self.bottom_w

class GameArea:
    def __init__(self):
        self.cells = urwid.Text("NW")
        self.antigens = urwid.Text("NE")
        self.cells_txt = urwid.Text("SW")
        self.antigens_txt = urwid.Text("SE")

        self.cells_col = urwid.Pile([
            (10, urwid.LineBox(urwid.Filler(self.cells))),
            urwid.LineBox(urwid.Filler(self.cells_txt)),
        ])

        self.antigens_col = urwid.Pile([
            (10, urwid.LineBox(urwid.Filler(self.antigens))),
            urwid.LineBox(urwid.Filler(self.antigens_txt)),
        ])

        self.body = urwid.Columns([self.cells_col, self.antigens_col])

    def selectable(self):
        return True
