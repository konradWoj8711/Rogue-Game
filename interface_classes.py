import pygame

class Button():
    def __init__(self, color, x, end_x, y, end_y, font, text='', alt_colour = None):
        self.color = color
        self.x = x
        self.y = y
        self.end_x = end_x - self.x
        self.end_y = end_y - self.y
        self.text = text
        self.font = font
        self.alt_colour = alt_colour

    def draw(self,win,mouse_pos,outline=None):
        #Call this method to draw the button on the screen
        if outline:
            pygame.draw.rect(win, outline, (self.x-2,self.y-2,self.end_x+4,self.end_y+4),0)

        pygame.draw.rect(win, self.color, (self.x,self.y,self.end_x,self.end_y),0)
        if mouse_pos:
            if self.check_pos(mouse_pos):
                pygame.draw.rect(win, self.alt_colour, (self.x,self.y,self.end_x,self.end_y),0)

        if self.text != '':
            text = self.font.render(self.text, 1, (0,0,0))
            win.blit(text, (self.x + (self.end_x/2 - text.get_width()/2), self.y + (self.end_y/2 - text.get_height()/2)))


    def isOver(self, pos):
        #Pos is the mouse position or a tuple of (x,y) coordinates
        if self.check_pos(pos):
            return True

        return False

    def check_pos(self,pos):
        if pos[0] > self.x and pos[0] < self.x + self.end_x:
            if pos[1] > self.y and pos[1] < self.y + self.end_y:
                return True
