import sys, pygame, time, serial, os, musicpy as mp, sf2_loader as sf, gpiozero, random

pygame.init()

root = os.path.dirname(__file__) + "\\"     # this is to help get data from image files


############### REPLACE SOUNDFONT TO RUN ON YOUR MACHINE ###############

loader = sf.sf2_loader(root+'Essential Keys-sforzando-v9.6.sf2')    # soundfont from - https://sites.google.com/site/soundfonts4u/
loader.load(root+'Essential Keys-sforzando-v9.6.sf2')

for x in range(16):
    loader.init_channel(x)

octave = '4'    # octave = str(int(octave)+1)

baseNotes = ['C', 'C#', 'D', 'D#', 'E', 'F',
            'F#', 'G', 'G#', 'A', 'A#', 'B']

const_decay=2
const_channel=0
const_start_time=0
const_piece_start_time=0
const_sample_width=2
const_channels=2
const_frame_rate=44100
const_name=None
const_format='wav'
const_bpm=80
const_fixed_decay=True
const_effects=None
const_pan=None
const_volume=100
const_length=1
const_extra_length=None
const_export_args={}

currentChord = []


'''
Button sytax goes:

[[Normal, Hover, Pressed],
 [Normal, Hover, Pressed,]]
'''

btnImages = [["normal.jpg", "hover.jpg", "pressed.jpg"]]

imgbuttonCount = 0  # this counts the ID number of the button class using images

objects = []

# window config
width, height = 800, 400
screen = pygame.display.set_mode((width, height))
font = pygame.font.SysFont('Arial', 40)





class Note():
    def __init__(self, pinNum, note):
        self.pinNum = pinNum
        self.note = note
   
    def buildChord(self):
        currentChord.append(self.note+octave)




# the basis for this class was from this tutorial - https://www.thepythoncode.com/article/make-a-button-using-pygame-in-python
class Button():
    def __init__(self, x, y, width, height, buttonText='Button', onclickFunction=None, imageButton=-1, onePress=False): # imageButton -1 will result in a text button

        if imageButton != -1:
            self.imgID = imageButton

            global btnImages
            self.normalImage = pygame.image.load(root+btnImages[self.imgID][0])
            self.hoverImage = pygame.image.load(root+btnImages[self.imgID][1])
            self.pressedImage = pygame.image.load(root+btnImages[self.imgID][2])

            print(btnImages[self.imgID][0])

        self.imageButton = imageButton
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.onclickFunction = onclickFunction
        self.onePress = onePress
        self.alreadyPressed = False


        self.fillColors = {
            'normal': '#6C4DE6',
            'hover': '#5940bd',
            'pressed': '#463294',
            }   


        self.buttonSurface = pygame.Surface((self.width, self.height))
        self.buttonRect = pygame.Rect(self.x, self.y, self.width, self.height)

        if imageButton == -1:
            self.buttonSurf = font.render(buttonText, True, (20, 20, 20))
        else:
            self.buttonSurf = pygame.transform.scale(self.normalImage, (self.width, self.height))

        objects.append(self)

    def chooseProcess(self):
        if self.imageButton == -1:
            self.txtProcess()
        else:
            self.imgProcess()


    def imgProcess(self):
        mousePos = pygame.mouse.get_pos()
        self.buttonSurf = pygame.transform.scale(self.normalImage, (self.width, self.height))
        if self.buttonRect.collidepoint(mousePos):
            self.buttonSurf = pygame.transform.scale(self.hoverImage, (self.width, self.height))
            if pygame.mouse.get_pressed(num_buttons=3)[0]:
                self.buttonSurf = pygame.transform.scale(self.pressedImage, (self.width, self.height))
                
                # very necessary
                self.buttonSurface.blit(self.buttonSurf, [      
                    self.buttonRect.width/2 - self.buttonSurf.get_rect().width/2,
                    self.buttonRect.height/2 - self.buttonSurf.get_rect().height/2
                ])
                screen.blit(self.buttonSurface, self.buttonRect)
                pygame.display.update()
                
                if self.onePress:
                    self.onclickFunction()
                elif not self.alreadyPressed:
                    self.onclickFunction()
                    self.alreadyPressed = True
            else:
                self.alreadyPressed = False

        self.buttonSurface.blit(self.buttonSurf, [
            self.buttonRect.width/2 - self.buttonSurf.get_rect().width/2,
            self.buttonRect.height/2 - self.buttonSurf.get_rect().height/2
        ])
        screen.blit(self.buttonSurface, self.buttonRect)
        

    def txtProcess(self):
        mousePos = pygame.mouse.get_pos()
        self.buttonSurface.fill(self.fillColors['normal'])

        if self.buttonRect.collidepoint(mousePos):
            self.buttonSurface.fill(self.fillColors['hover'])

            if pygame.mouse.get_pressed(num_buttons=3)[0]:
                self.buttonSurface.fill(self.fillColors['pressed'])

                
                # also very necessary
                self.buttonSurface.blit(self.buttonSurf, [      
                    self.buttonRect.width/2 - self.buttonSurf.get_rect().width/2,
                    self.buttonRect.height/2 - self.buttonSurf.get_rect().height/2
                ])
                screen.blit(self.buttonSurface, self.buttonRect)
                pygame.display.update()
                
                if self.onePress:
                    self.onclickFunction()
                elif not self.alreadyPressed:
                    self.onclickFunction()
                    self.alreadyPressed = True
            else:
                self.alreadyPressed = False

        self.buttonSurface.blit(self.buttonSurf, [
            self.buttonRect.width/2 - self.buttonSurf.get_rect().width/2,
            self.buttonRect.height/2 - self.buttonSurf.get_rect().height/2
        ])
        screen.blit(self.buttonSurface, self.buttonRect)





def inputchannelCycle():    # this was a way to try and make notes coming through not cut off the previous one, but it doesnt fix the issue
    global const_channel
    
    const_channel += 1
    if const_channel > 3:
        const_channel = 0

def playChord():
    print('\n', currentChord, '\n')
    loader.play_chord(sf.mp.chord(currentChord),
                        decay=const_decay,
                        channel=const_channel,
                        start_time=const_start_time,
                        piece_start_time=const_piece_start_time,
                        sample_width=const_sample_width,
                        channels=const_channels,
                        frame_rate=const_frame_rate,
                        name=const_name,
                        format=const_format,
                        bpm=const_bpm,
                        fixed_decay=const_fixed_decay,
                        effects=const_effects,
                        pan=const_pan,
                        volume=None,    # this doesn't work right now
                        length=const_length,
                        extra_length=const_extra_length,
                        export_args=const_export_args)

    inputchannelCycle()

def LightSensor(pin):
    return 0
    #return int(random.randint(0, 100) // 100)

def octaveUp():
    global octave
    octave = str(int(octave)+1)

def octaveDown():
    global octave
    octave = str(int(octave)-1)

lasers = [Note(x+12, baseNotes[x]) for x in range(12)]

keys = [Button(20+50*x+x*15, 50, 50, 50, lasers[x].note, lasers[x].buildChord, -1) for x in range(12)]

octaveUpbtn = Button(width/2-75, 200, 150, 50, 'Octave +', octaveUp, -1)
octaveDownbtn = Button(width/2-75, 300, 150, 50, 'Octave -', octaveDown, -1)




while True:
    tempTime=.02                # this is the amount of time in seconds used to collect the notes before it plays them
    while tempTime > 0:         # the point of doing it this way is to keep from having large amounts of time where input isnt being taken
        for laser in lasers:    # while also allowing time for the user to add multiple inputs to the same chord, which will sound better than singular notes
            if LightSensor(laser.pinNum) == 1:
                laser.buildChord()


        screen.fill((11, 17, 23))
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_q:
                    lasers[0].buildChord()
                if event.key == pygame.K_w:
                    lasers[1].buildChord()
                if event.key == pygame.K_e:
                    lasers[2].buildChord()
                if event.key == pygame.K_r:
                    lasers[3].buildChord()
                if event.key == pygame.K_t:
                    lasers[4].buildChord()
                if event.key == pygame.K_y:
                    lasers[5].buildChord()
                if event.key == pygame.K_u:
                    lasers[6].buildChord()
                if event.key == pygame.K_i:
                    lasers[7].buildChord()
                if event.key == pygame.K_o:
                    lasers[8].buildChord()
                if event.key == pygame.K_p:
                    lasers[9].buildChord()
                if event.key == pygame.K_LEFTBRACKET:
                    lasers[10].buildChord()
                if event.key == pygame.K_RIGHTBRACKET:
                    lasers[11].buildChord()
        

        for object in objects:
            object.chooseProcess()

        pygame.display.flip()

        time.sleep(.001)    # this is to allow time for updates to the chord to be played, every milisecond code checks for updates
        tempTime -= .001


    if len(currentChord) > 0:
        playChord()
        currentChord.clear()