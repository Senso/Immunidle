from random import choice, randrange
import time
import json
import urwid
from window import MainWindow

#import urwid.curses_display

### TODO
# X game pause
# antigens attacking (virus)
# antigens replicating
# python native 64-bit numbers?
# keypress for bigger/longer log window
# X programmed cell death
# mouse clicking for manual protein production?
# add a single option that scales down/up the game in speed (hp, seconds, defense, protein, etc.)

class Game:
    def __init__(self, data):
        self.data = data
        self.ticks = 0
        self.level = 0
        self.proteins = 0
        self.player_cells = []
        self.antigens = []
        self.msglog = ['','','','','']
        self.paused = False

    def display_log(self):
        return '\n'.join(self.msglog[-5:])

    def log(self, str):
        self.msglog.append(str)

    def initialize_player(self):
        # Start with a single random white cell
        name = choice(list(self.data['white cell']))
        c = Cell(name=name, data=self.data['white cell'][name], game=self)
        c.spawn()

        #self.player_cells.append(Cell('T helper', self.data['white cell']['T helper']))

    def initialize_level(self):
        for i in range(0, self.level):
            name = choice(list(self.data['antigen']))

            # multiply base_hp with the current level
            a = Antigen(name=name, data=self.data['antigen'][name], game=self)
            a.spawn()
            a.hp = a.hp * self.level

            #self.antigens.append(a)

    def check_level_state(self):
        if len(self.antigens) == 0:
            self.level += 1
            self.initialize_level()

    def dice_roll(self, min, max):
        total = 0
        total += randrange(min, max + 1)
        if total == max + 1:
            total += self.dice_roll(min, max)
        return total

    def flash(self, loop, target):
        target.palette = "flash %s" % target.palette
        loop.widget.mainloop.draw_antigens()
        loop.draw_screen()
        loop.set_alarm_in(0.2, self.unflash, target)

    def unflash(self, loop, target):
        target.palette = target.palette.replace('flash ', '')
        loop.widget.mainloop.draw_antigens()
        loop.draw_screen()

    def player_attack(self, mwin):
        for c in self.player_cells:
            if not self.antigens:
                return

            target = choice(self.antigens)

            # Calculate damage
            dmg = c.base_attack
            dmg += self.dice_roll(1, 3) # add some randomness
            dmg -= target.defense

            if dmg > 0:
                ### EXPERIMENTAL
                mwin.loop.set_alarm_in(0, self.flash, target)
                target.hp -= dmg

            self.log("%s dealt %s dmg to %s." % (c.name, dmg, target.name))

            if target.hp <= 0:
                target.die('killed by %s' % c.name)
                # Antigen dies/is absorbed
                #self.antigens.remove(target)

    def spawn_cell(self):
        # Cost grows the more cells you have
        base_cost = 10
        total_cost = base_cost + len(self.player_cells) * 20

        if self.proteins >= total_cost:
            name = choice(list(self.data['white cell']))
            c = Cell(name=name, data=self.data['white cell'][name], game=self)
            #self.player_cells.append(c)
            self.proteins -= total_cost
            self.log("%s cell purchased." % c.name)

    def age_all_cells(self):
        for c in self.player_cells:
            c.aging(1)


class Life(object):
    def __init__(self, name, game, data):
        self.name = name
        self.game = game
        self.data = data
        #self.spawn()

    def spawn(self):
        self.hp = self.data.get('base_hp', 1)
        self.defense = self.data.get('defense', 0)
        self.description = self.data.get('description', 'No description set')
        self.symbol = self.data.get('symbol', 'o')
        self.palette = self.data.get('palette', 'white')
        self.base_attack = self.data.get('base_attack', 0)
        self.lifespan = self.data.get('lifespan', 50)
        self.age = 0

        # Add ourself to the game world
        if type(self).__name__ == 'Cell':
            self.game.player_cells.append(self)
        elif type(self).__name__ == 'Antigen':
            self.game.antigens.append(self)
        else:
            self.game.log("Unknown %s tried to spawn." % type(self).__name__)

    def die(self, msg=None):
        if type(self).__name__ == 'Cell':
            self.game.player_cells.remove(self)
        elif type(self).__name__ == 'Antigen':
            self.game.antigens.remove(self)
        else:
            self.game.log("Unknown %s tried to die." % type(self).__name__)
        if msg:
            self.game.log("%s died %s." % (self.name, msg))

    def aging(self, amt=1):
        self.age += amt
        if self.age > self.lifespan:
            self.die('of old age')


class Antigen(Life):
    def __init__(self, name, game, data):
        super().__init__(name, game, data)

class Cell(Life):
    def __init__(self, name, game, data):
        super().__init__(name, game, data)


if __name__ == '__main__':
    json_fd = open('data.json', 'r')

    game = Game(json.load(json_fd))
    run = MainWindow(game)
    run.main()


