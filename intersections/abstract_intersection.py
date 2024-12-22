import io
import requests
import pygame

pygame.init()

# get some random image for the characters
characters_url = "https://upload.wikimedia.org/wikipedia/en/d/d6/Friends_season_one_cast.jpg"

# Define the characters data as a list of dictionaries.
# Each dictionary stores the name and the approximate part of the image that the character occupies.
W, H = 50, 60
characters_data = [{"name":"Joey","rect":(75,30, W, H)},
                   {"name":"Ross","rect":(180,30, W, H)},
                   {"name":"Monica","rect":(130,110, W, H)},  
                   {"name":"Chandler","rect":(230,40, W, H)},  
                   {"name":"Rachel","rect":(180,100, W, H)},  
                   {"name":"Phoebe","rect":(120,30, W, H)},      
]

class Character():
    font = pygame.font.Font(size=22)
    
    def __init__(self, name:str, rect:pygame.Rect):
        self.name = name
        self.rect = rect
        self.active = False
        self.display_name = Character.font.render(name,True, pygame.Color("white"), pygame.Color("blue"))
        
    def update(self, cursor_pos, screen:pygame.Surface):
        # set the instance to active based on the mouse position
        self.active = self.rect.collidepoint(cursor_pos)
        
        # blit a simple name to the screen
        if self.active:
            pygame.draw.rect(screen, pygame.Color("blue"), self.rect, width=1)
            screen.blit(self.display_name, self.rect.bottomleft)


def init():    
    # download the image
    bits = requests.get(characters_url, timeout = 1000)

    # create pygame surface from the downloaded image
    img = io.BytesIO(bits.content)
    background = pygame.image.load(img, "")
    screen = pygame.display.set_mode((background.get_width(), background.get_height()))
    
    # create a list of Character objects
    characters=[]
    for character in characters_data:
        l, t, w, h = character["rect"]
        characters.append(Character(name=character["name"], rect=pygame.Rect(l,t,w,h)))
        
    return screen, background, characters

def select():
    # get values from the init method
    screen, background, characters = init()
    
    # Nothing has been selected yet
    selected = None
    
    # Loop until a selection has been made    
    choosing = True
    while choosing:
        screen.blit(background,(0,0))
        mouse_pos = pygame.mouse.get_pos()

        for character in characters:
            character.update(mouse_pos, screen)
               
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                choosing = False
            
            # when the user makes a click, we check what was the character selected                
            if event.type == pygame.MOUSEBUTTONDOWN:
                for character in characters:
                    if character.active:
                        selected = character.name
                        choosing = False

        pygame.display.flip()

    return selected

# Call our select function and display the result in the console
selected = select()
if selected:
    print("The selected character was " + selected)

pygame.quit()