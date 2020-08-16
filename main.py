import pygame
import os
import time
import random
pygame.font.init()
pygame.mixer.init()

width,height = 600,600
WIN = pygame.display.set_mode((width,height))


SPACESHIP1 = pygame.image.load(os.path.join('assets','space-invaders.png')) # !main ship
SPACESHIP2 = pygame.image.load(os.path.join('assets','pixel_ship_blue_small.png'))
SPACESHIP3 = pygame.image.load(os.path.join('assets','pixel_ship_green_small.png'))
SPACESHIP4 = pygame.image.load(os.path.join('assets','pixel_ship_red_small.png'))

LASER1 = pygame.image.load(os.path.join('assets','pixel1.png'))

LASER2 = pygame.image.load(os.path.join('assets','pixel2.png'))

LASER3 = pygame.image.load(os.path.join('assets','pixel3.png'))

LASER4 = pygame.image.load(os.path.join('assets','pixel4.png'))

BACKG  = pygame.transform.scale(pygame.image.load(os.path.join('assets','back3.jpg')),(width,height))

pygame.mixer.music.load(os.path.join('assets','backtrack.wav'))

class Laser:
    def __init__(self,x,y,img):
        self.img = img
        self.x = x
        self.y = y
        self.mask = pygame.mask.from_surface(self.img)

    def draw(self,window):
        window.blit(self.img,(self.x,self.y))

    def move(self,vel):
        self.y += vel
    
    def screen_corner(self,height): # checks if the laser has reached the edges of screen
        return not(self.y <= height and self.y >=0)

    def collision(self,obj): #checks if any object collides with a particular ship(player/enemy)  
        return collide(self,obj) 

class Ship:
    COOLDOWN = 60
    def __init__(self,x,y,health=100): # defining the attributes of each ship
        self.x = x   # x coordinate
        self.y = y  # y coordinate 
        self.health =  health  # initial health 
        self.image = None # ship image (representation)
        self.laser_img = None # image for the lasers coming right from the ship
        self.laserlist = [] # 
        self.cool_down_timer = 0 #

    def draw(self,window):
        window.blit(self.image,(self.x,self.y))
        for laser in self.laserlist:
            laser.draw(window)
        # pygame.draw.rect(window,(200,0,0),(self.x,self.y,50,50)) # location of the rectangle
    
    
    def get_width(self):
        return self.image.get_width()

    def get_height(self):
        return self.image.get_height()

    
    def cooldown(self): # to check if the cooldown time is over
        if self.cool_down_timer >= self.COOLDOWN:
            self.cool_down_timer = 0
        elif self.cool_down_timer > 0:
            self.cool_down_timer += 1

    def move(self,vel):
        self.y += vel

    def move_lasers(self,vel,obj): #check if each laser has hit any objects in a list 
        self.cooldown()
        for laser in self.laserlist:
            laser.move(vel)
            if laser.screen_corner(height):
                self.laserlist.remove(laser)
            elif laser.collision(obj):
                obj.health -= 10
                if laser in self.laserlist:
                    self.laserlist.remove(laser)

                
    def shoot(self):
        if self.cool_down_timer == 0:
            laser = Laser(self.x,self.y,self.laser_img)
            self.laserlist.append(laser)
            self.cool_down_timer = 1



class Player(Ship):
    def __init__(self,x,y,health=100):
        super().__init__(x,y,health)
        self.image = SPACESHIP1
        self.laser_img = LASER1
        self.mask = pygame.mask.from_surface(self.image) # for pixel2pixel accuracy
        self.max_health  = health

    def move(self,vel):
        self.y += vel

    def draw(self,window):
        super().draw(window)
        self.healthbar(window)

    def move_lasers(self,vel,objs): #check if each laser has hit the 
        self.cooldown()
        for laser in self.laserlist:
            laser.move(vel)
            if laser.screen_corner(height):
                self.laserlist.remove(laser)
            else:
                for obj in objs:
                    if laser.collision(obj):
                        objs.remove(obj)
                        self.laserlist.remove(laser)

    def shoot(self):
        if self.cool_down_timer == 0:
            laser = Laser(self.x -15 ,self.y -15 ,self.laser_img)
            self.laserlist.append(laser)
            self.cool_down_timer = 1

    def healthbar(self,window):
        # pygame.draw.rect()
        pygame.draw.rect(window,(255,0,0),(self.x  ,self.y + self.image.get_height() + 10,self.image.get_width(),10))
        pygame.draw.rect(window,(0,250,0),(self.x,self.y + self.image.get_height()+10, self.image.get_width()*(self.health/self.max_health),10)) 
    
class Enemy(Ship):
    image_dict = {
        'red':(SPACESHIP2,LASER2),
        'green':(SPACESHIP3,LASER3),
        'blue':(SPACESHIP4,LASER4)
    }
    # print(image_dict)

    def __init__(self,x,y,color,health=100):
        super().__init__(x,y,health)
        self.image,self.laser_img = self.image_dict[color]
        self.mask = pygame.mask.from_surface(self.image)

    def shoot(self):
        if self.cool_down_timer == 0:
            laser = Laser(self.x -15 ,self.y -15 ,self.laser_img)
            self.laserlist.append(laser)
            self.cool_down_timer = 1




def collide(obj1,obj2): 
    offset_x = obj2.x - obj1.x
    offset_y = obj2.y - obj1.y 
    return obj1.mask.overlap(obj2.mask,(offset_x,offset_y)) != None




def main():
    pygame.mixer.music.play(-1)
    level = 0 
    lives = 2
    font1 = pygame.font.Font(os.path.join('assets','amatic.ttf'),40) # FONT for LEVELS and LIVES
    lost_font = pygame.font.Font(os.path.join('assets','amatic.ttf'),60) # LOST MESSAGE
    running = True # whether app is running or not
    player_velocity = 6 # velo
    FPS = 120 # Frames p sec
    player = Player(300,500) # player coords
    lost_seconds = 0 # time spent displaying the lost message on the screen
    lost = False
    pause_font = pygame.font.Font(os.path.join('assets','amatic.ttf'),50) # when the game is paused
    enemies = [] # list of enemies
    wave_length = 5 # how long the eave of enemies supposed to be
    enemy_vel = 1
    laser_vel_player = -6
    laser_vel = 3
    clock = pygame.time.Clock()
    pause = False
    lost_message = lost_font.render('You lost!!',1,(100,150,150))

    def redraw_window():
        nonlocal pause
        nonlocal lost_message
        '''
        Function to draw stuff on the panel (refreshes) 
        '''
        WIN.blit(BACKG,(0,0))

        lives_capt = font1.render(f'Lives : {lives}',True,(255,255,255)) #for captions 
        level_capt = font1.render(f'Level : {level}',True,(255,255,255)) #for captions
        m = font1.render('Hello',True,(200,200,120),None)
        WIN.blit(lives_capt,(10,10)) # displaying the element (LIVES)
        WIN.blit(level_capt,(width - level_capt.get_width() - 10 , 10)) # displaying the element (LEVELS)

        if lost:
            lost_message = lost_font.render('You lost!!',1,(250,150,150))
            WIN.blit(lost_message,(width/2 - lost_message.get_width()/2,300))

        if pause:
            pause_message = pause_font.render("Game has been paused ,",1,(200,150,150))
            pause_message2 = pause_font.render(" Press space to resume.",1,(200,150,150))
            WIN.blit(pause_message,(width/2 - pause_message.get_width()/2,300))
            WIN.blit(pause_message2,(width/2 - pause_message.get_width()/2,350))
            running =False
                

        for enemy in enemies:
            enemy.draw(WIN) 


        player.draw(WIN)
    

        pygame.display.update()



    while running: # the program is running

        clock.tick(FPS)
        redraw_window()



        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                quit()

        keys_list = pygame.key.get_pressed()

        if lives <=0 or player.health<0:
            pygame.mixer.music.stop()
            lost = True
            lost_seconds+=1

        if pause:

            if keys_list[pygame.K_SPACE]:
                pause  = False
                pygame.mixer.music.unpause()
            else:

                continue


        if lost:
            if lost_seconds> FPS*3:
                running = False
            else:
                continue
        
            

        if len(enemies) == 0:
            level +=1
            wave_length +=5
            enemy_vel +=1
            for i in range(wave_length):
                enemy = Enemy(random.randrange(50,width-100),random.randrange(-600*(1.2)*(i+1),-50),random.choice(['red','blue','green']))
                enemies.append(enemy)
                
        if keys_list[pygame.K_ESCAPE]:
            pause = True 
            pygame.mixer.music.pause()


        if keys_list[pygame.K_UP] and player.y - player_velocity > 0 :
            player.y -= player_velocity 

        if keys_list[pygame.K_DOWN] and player.y + player_velocity + player.get_height() + 15 <height:
            player.y += player_velocity
        
        if keys_list[pygame.K_LEFT] and player.x - player_velocity > 0:
            player.x -= player_velocity
         
        if keys_list[pygame.K_RIGHT] and player.x + player_velocity + player.get_width() <width:
            player.x += player_velocity

        if keys_list[pygame.K_SPACE]:
            player.shoot() 

        for enemy in enemies[:]: 
            enemy.move(enemy_vel)
            enemy.move_lasers(laser_vel,player)
            
            
            if random.randrange(0,120) == 1:
                enemy.shoot()

            if collide(enemy,player):
                player.health -=10
                enemies.remove(enemy)            
            
            
            if enemy.y + enemy.get_height() > height:
                lives -=1
                level +=1
                enemies.remove(enemy)
                # print(len(enemies))

        player.move_lasers(laser_vel_player,enemies)


def main_menu():
    title_font = pygame.font.Font(os.path.join('assets','amatic.ttf'),50)
    run = True
    while run:
        WIN.blit(BACKG, (0,0))
        title_label = title_font.render("Press F to begin...", 1, (200,150,150))
        WIN.blit(title_label, (width/2 - title_label.get_width()/2, 350))
        pygame.display.update()
        keys_list = pygame.key.get_pressed()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
            if keys_list[pygame.K_f]:
                main()

    pygame.quit()


# main()
main_menu()