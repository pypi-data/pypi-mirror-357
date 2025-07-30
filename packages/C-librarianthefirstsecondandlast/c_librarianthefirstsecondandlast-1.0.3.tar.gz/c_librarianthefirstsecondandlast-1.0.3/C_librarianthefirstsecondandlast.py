from math import *
import inspect
import pygame as pg

def point_on_segment(point:list[float, float], line:list[list, list]):
    """Outputs True if a given point is found on a line segment."""
    # Finding line equation starting with m
    # y = mx + c
    try:
        m1 = (line[0][1] - line[1][1])/(line[0][0] - line[1][0])

    except ZeroDivisionError:
        # Including provision for vertical lines with infinite gradient
        m1 = "inf"
        
     
    if m1 == "inf":  
        # If gradient is infinite line equation becomes x = c 
        c1 = line[0][0]
        # Finding whether the point lies on the line and fits on the segment
        
        if point[0] == c1 and (line[1][1] >= point[1] >= line[0][1] or line[1][1] <= point[1] <= line[0][1]):
            return True
        
        else:
            return False
        
    else:
        # Finding c with the rearanged equation c = y - mx
        c1 = line[0][1] - m1*line[0][0]
    
        # Finding whether the point lies on the line and fits on the segment
        if (line[1][0] >= point[0] >= line[0][0] or line[1][0] <= point[0] <= line[0][0]) and (line[1][1] >= point[1] >= line[0][1] or line[1][1] <= point[1] <= line[0][1]):
            
            return True
        
        else:
            return False   

def line_intersect(line_a:list[list[float, float], list[float, float]], line_b:list[list[float, float], list[float, float]]):
    """Outputs the point at which 2 straight lines intersect."""
    try:
        #finding gradient of line
        m1 = (line_a[0][1] - line_a[1][1])/(line_a[0][0] - line_a[1][0])

    except ZeroDivisionError:
        # Provision for vertical lines
        m1 = "inf"
      
    # Same as last one  
    try:
        m2 = (line_b[0][1] - line_b[1][1])/(line_b[0][0] - line_b[1][0])

    except ZeroDivisionError:
        m2 = "inf"
     
    if m1 == "inf":   
        c1 = line_a[0][0]
        
    else:
        c1 = line_a[0][1] - m1*line_a[0][0]
        
    if m2 == "inf":   
        c2 = line_b[0][0]
        
    else:
        c2 = line_b[0][1] - m2*line_b[0][0]
    
    if m1 == m2:
        return None
    
    if m1 == "inf":
        x = c1
        y = (m2*c1) + c2
        
    elif m2 == "inf":
        x = c2
        y = (m1*c2) + c1
    
    else:
        x = (c1 - c2)/(m2-m1)
        y = m1*x + c1
        
    
    return (round(x, 5), round(y, 5))
    
def distance(a, b):
    """Returns distance between two points."""
    x = a[0] - b[0]
    y = a[1] - b[1]
    
    c = (x**2 + y**2)**0.5
    return c

def angle_from(a, b):
    """Gives the angle FROM a TO b."""
    x_diff = b[0] - a[0]
    y_diff = b[1] - a[1]
    
    vector = x_diff, y_diff
    
    angle = angle_from_vector(vector)
            
    return angle
    
def angle_from_vector(vector: tuple[float, float]):
    """Returns angle of a vector in RADIANS"""
    x, y = vector
    
    angle = atan2(y, x)
            
    return angle
    
def vector_from(a, b):
    """Gives the vector FROM a TO b."""
    
    x_diff = b[0] - a[0]
    y_diff = b[1] - a[1]

    vector = x_diff, y_diff
    
    return vector

def normalise(vector):
    magnitude = vector_magnitude(vector)
    n_vector = [vector[0]/magnitude, vector[1]/magnitude]
    
    return(n_vector)

def normalised_dot(a, b):
    """Outputs the dot product of two vectors, after normalising."""
    a = normalise(a)
    b = normalise(b)
    
    c = dot(a, b)
    
    return c

def dot(a, b):
    """Outputs the dot product of two vectors"""
    
    c = a[0] * b[0] + a[1] * b[1]
    
    return c

def vector_projection(a, b):
    """Returns the projection of vector A onto vector B."""
    c = vector_magnitude(b)
    d = dot(a, b)

    e = [d/(c**2) * b[0], d/(c**2) * b[1]] 
    return e 

def absolute(x):
    """Returns the absolute value of x."""
    x = x**2
    x = x**0.5
    
    return x

def vector_magnitude(vector):
    """Outputs the magnitude of a vector."""
    length = (vector[0]**2 + vector[1]**2)**0.5
    
    return length

def vector_from_angle(angle):
    "Gives a normalised vector from an angle given in degrees."
    angle = radians(angle)
    
    vector = [round(sin(angle), 10), round(cos(-angle), 10)]
    
    return vector


class button():
    def __init__(self, display: pg.window.Window, width: float, height: float, 
                 center: tuple[float, float], outer_colour: tuple[int, int, int], 
                 inner_colour: tuple[int, int, int], text: str = "", max_width: int = 0, 
                 max_height: int = 0, thickness: int = 5, text_colour: tuple[int, int, int] = (0, 0, 0),
                 slider = False, slider_max = -1, slider_min = -1,
                 slider_value = -1, slider_colour = (0, 0, 0),
                 radius = 100) -> None:
        
        self.display = display.get_surface()
        self.width = width
        self.height = height
        self.center = center
        
        self.outer_colour = outer_colour
        self.inner_colour = inner_colour
        self.font = pg.font.SysFont("Calibri", 200)
        self.text = text
        self.text_colour = text_colour
        
        self.max_width = max_width
        self.max_height = max_height
        self.thickness = thickness
        self.slider = slider
        self.slider_max = slider_max
        self.slider_min = slider_min
        self.slider_value = slider_value
        self.slider_colour = slider_colour
        if radius == -1:
            self.radius = self.thickness
        else:
            self.radius = radius        
        
    def draw(self):
        if self.slider == True and self.radius > 20:
            self.radius = 20
        center = self.center[0]*self.display.get_width(), self.center[1]*self.display.get_height()
        width = self.width*self.display.get_width()
        height = self.height*self.display.get_height()
        
        t_s = self.font.render(self.text, True, self.text_colour)
        
        pg.draw.rect(self.display, self.outer_colour,
                     (center[0]-(width/2), center[1]-(height/2),
                      width, height), border_radius=self.radius)
        pg.draw.rect(self.display, self.inner_colour,
                     (center[0]-(width/2)+self.thickness,
                      center[1]-(height/2)+self.thickness,
                      width-(2*self.thickness), height-(2*self.thickness))
                     , border_radius=self.radius)
        if self.slider == True:
            pg.draw.rect(self.display, self.outer_colour,
                         (center[0]-((width-10)/2)+self.thickness, center[1]-(height/2)+self.thickness+(0.5*height),
                          width-(2*self.thickness)-10, (height-(2*self.thickness))*0.25), border_radius=self.radius
                         )
            pg.draw.rect(self.display, self.inner_colour,
                         (center[0]-((width-10)/2)+self.thickness+5, center[1]-(height/2)+self.thickness+(0.5*height)+5,
                          width-(2*self.thickness)-20, (height-(2*self.thickness))*0.25-10), border_radius=self.radius
                         )
            range = self.slider_max - self.slider_min
            ratio = self.slider_value/range
            pg.draw.rect(self.display, self.outer_colour,
                         (center[0]-((width-10)/2)+self.thickness+5, center[1]-(height/2)+self.thickness+(0.5*height)+5,
                          ratio*(width-(2*self.thickness)-20), (height-(2*self.thickness))*0.25-10)
                         )
            pg.draw.rect(self.display, self.slider_colour,
                         ((center[0]-((width-10)/2)+self.thickness) + (ratio*(width-(2*self.thickness)-15)), center[1]-(height/2)+self.thickness+(0.5*height)-15,
                          10, ((height-(2*self.thickness))*0.25)+30), border_radius=self.radius
                         )
            pg.draw.rect(self.display, self.inner_colour,
                         ((center[0]-((width-10)/2)+self.thickness) + (ratio*(width-(2*self.thickness)-13)), center[1]-(height/2)+self.thickness+(0.5*height)-13,
                          8, ((height-(2*self.thickness))*0.25)+26), border_radius=self.radius
                         )
            t_s = pg.transform.scale(t_s, (width-(2*self.thickness), (height/2)-(2*self.thickness)))
        else:
            t_s = pg.transform.scale(t_s, (width-(2*self.thickness), (height)-(2*self.thickness)))
            
        self.display.blit(t_s, (center[0]-(width/2)+self.thickness, (center[1]-(height/2)+self.thickness) + (0.1*height)))
    
    def get_focused(self, pos: tuple[int, int]) -> bool|list[bool,float]:
        center = self.center[0]*self.display.get_width(), self.center[1]*self.display.get_height()
        width = self.width*self.display.get_width()
        height = self.height*self.display.get_height()
        
        if pos[0] > center[0]-(0.5*width) and pos[0] < center[0]+(0.5*width) and pos[1] > center[1]-(0.5*height) and pos[1] < center[1]+(0.5*height):
            if self.slider == False:
                return True
            else:
                # min = center[0]-((width-10)/2)+self.thickness+5, max = center[0]-((width-10)/2)+self.thickness+5 + width-(2*self.thickness)-20
                range = width-(2*self.thickness)-20
                
                selected_pos = pos[0] - (center[0]-((width-10)/2)+self.thickness+5)
                selected_val = selected_pos/range
                actual_val = selected_val * self.slider_max
                if actual_val < self.slider_min:
                    actual_val = self.slider_min
                elif actual_val > self.slider_max:
                    actual_val = self.slider_max
                
                return [True, actual_val]
        else:
            if self.slider == True:
                return [False, None]
            else:
                return False
        
def warn(warning:str):
    """Returns a list of all identical warnings as well as the line number of the warning.
       Only accepts raw string data, it WILL NOT WORK if a variable is given."""
    file = open(inspect.stack()[1].filename,'r')   
    lines = file.readlines()
    file.close()
    
    count = 0
    for line in lines:
        count +=1
        if "warn('"+str(warning)+"')" in line or 'warn("'+str(warning)+'")' in line:
            print(warning+" at line "+str(count)+".")
  

