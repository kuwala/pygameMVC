#! /usr/bin/env python
# Based on a Tutorial by sjbrown
# http://ezide.com/games/writing-games.html
import random

DIRECTION_UP = 0
DIRECTION_DOWN = 1
DIRECTION_LEFT = 2
DIRECTION_RIGHT = 3

def Debug( msg ):
  print (msg)

class Event:
  """This is a superclass for any events that might
  be generated by an object and sent to the EventManager
  """
  def __init__(self):
    self.name = "Generic Event"

class TickEvent(Event):
  def __init__(self):
    self.name = "CPU Tick Event"
class QuitEvent(Event):
  def __init__(self):
    self.name = "Program Quit Event"
class MapBuiltEvent(Event):
  def __init__(self, gameMap):
    self.name = "Map Finished Building Event"
    self.gameMap = gameMap
class GameStartedEvent(Event):
  def __init__(self, game):
    self.name = "Game Started Event"
    self.game = game
class CharactorMoveRequest(Event):
  def __init__(self, direction):
    self.name = "Character Move Request"
    self.direction = direction

class CharactorPlaceEvent(Event):
  """this event occurs when a Charactor is PLACED in a 
  sector, it dosen't move there from neighbor sector."""
  def __init__(self, charactor):
    self.name = "Character Placement Event"
    self.charactor = charactor
class CharactorMoveEvent(Event):
  def __init__(self, charactor):
    self.name = "Charactor Move Event"
    self.charactor = charactor

class EventManager:
  """This object is responsible for coordinating most communication
  between the Model, View, and Controller
  """
  def __init__(self):
    from weakref import WeakKeyDictionary
    self.listeners = WeakKeyDictionary()
  def RegisterListener(self, listener):
    self.listeners[listener] = 1

  def UnregisterListener(self, listener):
    if listener in self.listeners.keys():
      del self.listeners[ listener ]

  def Post(self, event):
    """Post a new event. It will be broadcast to all listeners"""
    if not isinstance(event, TickEvent):
      Debug( "        Message: " + event.name )
    for listener in self.listeners.keys():
      #Note: if the weakref has died, it will
      #be automatically removed, so we dont
      #have to worry about it
      listener.Notify(event)
class KeyboardController:
  """KeyboardController takes Pygame events generated by the
  keyboard and uses them to control the model, by sending Requests
  or to control the Pygame dislay directly, as with the QuitEvent
  """
  def __init__(self, evManager):
    self.evManager = evManager
    self.evManager.RegisterListener(self)

  def Notify(self, event):
    if isinstance( event, TickEvent ):
      #Handle Input Events
      for event in pygame.event.get():
        ev = None
        if event.type == QUIT:
          ev = QuitEvent()
        elif event.type == KEYDOWN and event.key == K_ESCAPE:
          ev = QuitEvent()
        elif event.type == KEYDOWN and event.key == K_DOWN:
          direction = DIRECTION_DOWN
          ev = CharactorMoveRequest(direction)
        elif event.type == KEYDOWN and event.key == K_LEFT:
          direction = DIRECTION_LEFT
          ev = CharactorMoveRequest(direction)
        elif event.type == KEYDOWN and event.key == K_RIGHT:
          direction = DIRECTION_RIGHT
          ev = CharactorMoveRequest(direction)
        elif event.type == KEYDOWN and event.key == K_UP:
          direction = DIRECTION_UP
          ev = CharactorMoveRequest(direction)

        if ev:
          self.evManager.Post( ev )

class CPUSpinnerController:
  """..."""
  def __init__(self, evManager):
    self.evManager = evManager
    self.evManager.RegisterListener( self )
    self.keepGoing = 1
  def Run(self):
    while self.keepGoing:
      ev = TickEvent()
      self.evManager.Post( ev )
  def Notify(self, event):
    if isinstance( event, QuitEvent ):
      self.keepGoing = False

# - - - - - - - - - - - - - - 
import pygame
from pygame.locals import *


class SectorSprite(pygame.sprite.Sprite):
  def __init__(self, sector, group=None):
    pygame.sprite.Sprite.__init__(self, group)
    self.image = pygame.Surface( (128, 128) )
    self.image.fill( (0,255,128) )

    self.sector = sector
  def update(self):
    self.image.fill( (random.randint(0,255),200,200) )

class CharactorSprite(pygame.sprite.Sprite):
  def __init__(self, group=None):
    pygame.sprite.Sprite.__init__(self, group)

    charactorSurf = pygame.Surface( (64,64) )
    charactorSurf = charactorSurf.convert_alpha()
    charactorSurf.fill( (0,0,0,0)) #make transparent

    #circle( destSurface, color, pos, radius, width=0)
    #width at 0 means the circle will be filled
    pygame.draw.circle( charactorSurf, (255,0,0), (32,32), 32)
    self.image = charactorSurf
    self.rect = charactorSurf.get_rect()

    self.moveTo = None

  def update(self):
    if self.moveTo:
      self.rect.center = self.moveTo
      self.moveTo = None
      print("moved")

class PygameView:
  def __init__(self, evManager):
    self.evManager = evManager
    self.evManager.RegisterListener(self)
    # 
    pygame.init()
    # self.window is simmilar to screen
    self.window = pygame.display.set_mode( (424, 440) )
    pygame.display.set_caption('pygameMVC')
    self.background = pygame.Surface( self.window.get_size() )
    self.background.fill( (0,0,0) )
    font = pygame.font.Font(None, 30)
    text = """Press SPACE BAR to start"""
    textImg = font.render( text, 1, (255,0,0))
    self.background.blit( textImg, (0,0) )
    self.window.blit( self.background, (0,0) )
    pygame.display.flip()

    self.backSprites = pygame.sprite.RenderUpdates()
    self.frontSprites = pygame.sprite.RenderUpdates()

  def ShowMap(self, gameMap):
    #clear screen first
    self.background.fill( (0,0,0) )
    self.window.blit( self.background, (0,0) )
    pygame.display.flip()

    # use squareRect as a cursor and go through the
    # columns and rows and assign the rect
    # positions of the SectorSprites with 10px padding
    #
    # { }[ ] [ ] [ ]   
    #    [ ] [ ] [ ]   
    #    [ ] [ ] [ ]   

    # { } - starting to the left of the screen 
    squareRect = pygame.Rect( (-128,10, 128,128) )
    column = 0
    for sector in gameMap.sectors:
      if column < 3:
        # move the rect to the right
        squareRect = squareRect.move( 138, 0 ) 
      else:
        column = 0
        squareRect = squareRect.move( -(138*2), 138 )
      column += 1
      newSprite = SectorSprite( sector, self.backSprites )
      newSprite.rect = squareRect
      newSprite = None

  def ShowCharactor(self, charactor):
    sector = charactor.sector
    charactorSprite = CharactorSprite( self.frontSprites )
    sectorSprite = self.GetSectorSprite( sector )
    charactorSprite.rect.center = sectorSprite.rect.center

  def MoveCharactor(self, charactor):
    charactorSprite = self.GetCharactorSprite( charactor )
    sector = charactor.sector
    sectorSprite = self.GetSectorSprite( sector )
    # moveTo updates the sprite.rect.center when charactor is update()
    charactorSprite.moveTo = sectorSprite.rect.center
    print(sectorSprite.rect.center)
    print(charactorSprite.moveTo)

  def GetCharactorSprite(self, charactor):
    # There will be only one
    for s in self.frontSprites:
      print("got charactor")
      return s
    print("didnt find charactor")
    return None

  def GetSectorSprite(self, sector):
    for s in self.backSprites:
      if hasattr(s, "sector") and s.sector == sector:
        return s
  def Notify(self, event):
    if isinstance( event, TickEvent ):
      #Draw Everthing
      #Redraw the background where the sprites used to be
      self.backSprites.clear(self.window, self.background)
      self.frontSprites.clear(self.window, self.background)

      self.backSprites.update()
      self.frontSprites.update()

      # Draw the sprites and save a list of Rects
      # where the sprites where updated
      dirtyRects1 = self.backSprites.draw( self.window )
      dirtyRects2 = self.frontSprites.draw( self.window )
      
      # update the screen just where the sprites where drawn
      dirtyRects = dirtyRects1 + dirtyRects2
      pygame.display.update( dirtyRects )

    elif isinstance( event, MapBuiltEvent ):
      gameMap = event.gameMap
      self.ShowMap( gameMap )
    elif isinstance( event, CharactorPlaceEvent ):
      self.ShowCharactor( event.charactor )
    elif isinstance( event, CharactorMoveEvent ):
      self.MoveCharactor( event.charactor )

class Game:
  """..."""
  STATE_PREPARING = 'preparing'
  STATE_RUNNING = 'running'
  STATE_PAUSED = 'paused'

  def __init__(self, evManager):
    self.evManager = evManager
    self.evManager.RegisterListener( self )

    self.state = Game.STATE_PREPARING

    self.players = [ Player(evManager) ]
    self.map = Map( evManager )

  def Start(self):
    self.map.Build()
    self.state = Game.STATE_RUNNING
    ev = GameStartedEvent( self )
    self.evManager.Post ( ev )

  def Notify(self, event):
    if isinstance( event, TickEvent ):
      if self.state == Game.STATE_PREPARING:
        self.Start()
class Player(object):
  """..."""
  def __init__(self, evManager):
    self.evManager = evManager
    self.game = None
    self.name = ""
    self.evManager.RegisterListener( self )
    self.charactors = [ Charactor(evManager) ]

  def __str__(self):
    return '<Player %s %s>' % (self.name, id(self))
  def Notify(self, event):
    pass

class Charactor:
  """..."""
  STATE_INACTIVE = 0
  STATE_ACTIVE = 1

  def __init__(self, evManager):
    self.evManager = evManager
    self.evManager.RegisterListener( self )

    self.sector = None
    self.state = Charactor.STATE_INACTIVE
  def __str__(self):
    return '<Charactor %s>' % id(self)

  def Move(self, direction):
    if self.state == Charactor.STATE_INACTIVE:
      return
    if self.sector.MovePossible( direction ):
      newSector = self.sector.neighbors[direction]
      self.sector = newSector
      ev = CharactorMoveEvent( self )
      self.evManager.Post( ev )

  def Place(self, sector):
    self.sector = sector
    self.state = Charactor.STATE_ACTIVE

    ev = CharactorPlaceEvent( self )
    self.evManager.Post( ev )

  def Notify(self, event):
    if isinstance(event, GameStartedEvent ):
      gameMap = event.game.map
      self.Place( gameMap.sectors[gameMap.startSectorIndex] )
    elif isinstance( event, CharactorMoveRequest ):
      self.Move( event.direction )

class Map:
  """..."""

  STATE_PREPARING = 0
  STATE_BUILT = 1

  def __init__(self, evManager):
    self.evManager = evManager
    #self.evManager.RegisterListener(self)

    self.state = Map.STATE_PREPARING
    self.sectors = []
    self.startSectorIndex = 0

  def Build(self):
    for i in range(9):
      self.sectors.append( Sector(self.evManager) )

    #    [0] [1] [2]   
    #    [3] [4] [5]   
    #    [6] [7] [8] 

    self.sectors[3].neighbors[DIRECTION_UP] = self.sectors[0]
    self.sectors[4].neighbors[DIRECTION_UP] = self.sectors[1]
    self.sectors[5].neighbors[DIRECTION_UP] = self.sectors[2]
    self.sectors[6].neighbors[DIRECTION_UP] = self.sectors[3]
    self.sectors[7].neighbors[DIRECTION_UP] = self.sectors[4]
    self.sectors[8].neighbors[DIRECTION_UP] = self.sectors[5]

    self.sectors[0].neighbors[DIRECTION_DOWN] = self.sectors[3]
    self.sectors[1].neighbors[DIRECTION_DOWN] = self.sectors[4]
    self.sectors[2].neighbors[DIRECTION_DOWN] = self.sectors[5]
    self.sectors[3].neighbors[DIRECTION_DOWN] = self.sectors[6]
    self.sectors[4].neighbors[DIRECTION_DOWN] = self.sectors[7]
    self.sectors[5].neighbors[DIRECTION_DOWN] = self.sectors[8]

    self.sectors[1].neighbors[DIRECTION_LEFT] = self.sectors[0]
    self.sectors[2].neighbors[DIRECTION_LEFT] = self.sectors[1]
    self.sectors[4].neighbors[DIRECTION_LEFT] = self.sectors[3]
    self.sectors[5].neighbors[DIRECTION_LEFT] = self.sectors[4]
    self.sectors[7].neighbors[DIRECTION_LEFT] = self.sectors[6]
    self.sectors[8].neighbors[DIRECTION_LEFT] = self.sectors[7]

    self.sectors[0].neighbors[DIRECTION_RIGHT] = self.sectors[1]
    self.sectors[1].neighbors[DIRECTION_RIGHT] = self.sectors[2]
    self.sectors[3].neighbors[DIRECTION_RIGHT] = self.sectors[4]
    self.sectors[4].neighbors[DIRECTION_RIGHT] = self.sectors[5]
    self.sectors[6].neighbors[DIRECTION_RIGHT] = self.sectors[7]
    self.sectors[7].neighbors[DIRECTION_RIGHT] = self.sectors[8]

    self.state = Map.STATE_BUILT

    ev = MapBuiltEvent( self )
    self.evManager.Post( ev )

class Sector(object):
  """..."""
  def __init__(self, evManager):
    self.evManager = evManager
    #self.evManager.RegisterListener( self )

    self.neighbors = [range(4)]
    for i in range(4):
      self.neighbors.append( None )


    self.neighbors[DIRECTION_UP] = None
    self.neighbors[DIRECTION_DOWN] = None
    self.neighbors[DIRECTION_LEFT] = None
    self.neighbors[DIRECTION_RIGHT] = None

  def MovePossible(self,direction):
    if self.neighbors[direction]:
      return 1

def main():
  """..."""
  evManager = EventManager()
  keybd = KeyboardController( evManager )
  spinner = CPUSpinnerController( evManager )
  pygameView = PygameView( evManager )
  game = Game( evManager )

  spinner.Run()

if __name__ == "__main__":
  main()



# - - - - -  - - This will be useless soon - - - -  - - -  -
"""
while not done:
  if not ControllerTick():
    break
  ViewTick()

  clock.tick(60)

print("Closing pygame")
pygame.quit()
print("Exited")

"""

