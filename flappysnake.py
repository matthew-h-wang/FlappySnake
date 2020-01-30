import pyglet
import random
pyglet.resource.path =['./images']
pyglet.resource.reindex()

game_window = pyglet.window.Window()

greensquare_image = pyglet.resource.image("greensquare.png")
upperwall_image = pyglet.resource.image("bluesquare.png")
lowerwall_image = pyglet.resource.image("bluesquare.png")

score_label = pyglet.text.Label(text= "Score: 0", x = 10, y = 460)
level_label = pyglet.text.Label(text="Click to start",
                            x=game_window.width//2, y=game_window.height//2, anchor_x='center')

main_batch = pyglet.graphics.Batch()

walls = []
initial_speed = 250
speed = initial_speed
wall_interval = 3
wall_opening = 150

food = []
food_freq = 1

gravity = .6
jump_vel = 10
tail_jump_vel = 11
min_fall_vel_to_jump = 2
max_fall_vel = 8

player_snake = None #pyglet.sprite.Sprite(img=greensquare_image, x = greensquare_image.width, y=game_window.height//2, batch=main_batch)
# player_snake.vel_y = jump_vel

score = 0
level = 1

snake_tail = []

#Create the upper and lower parts of a new wall on the right side with
#a random height and a given opening size
# adds to batch if provided
def makeWallPair(opening_size, batch = None):
    upper_opening_y = random.randint(opening_size,game_window.height)
    lower_opening_y = upper_opening_y - opening_size

    wall_upper = pyglet.sprite.Sprite(img=upperwall_image,x=game_window.width,
                                      y = upper_opening_y , batch = batch)

    wall_lower = pyglet.sprite.Sprite(img=lowerwall_image,x=game_window.width,
                                      y = lower_opening_y - lowerwall_image.height, batch = batch)
    walls.append(wall_upper)
    walls.append(wall_lower)
    return lower_opening_y

#rectangular collisions
def collides_with(sprite1, sprite2):
    if not (sprite1 and sprite2):
        return False
    if sprite1.x > (sprite2.x + sprite2.width): # s1 is right of s2
        return False
    if sprite2.x > (sprite1.x + sprite1.width): #s1 is left of s2
        return False
    if sprite1.y > (sprite2.y + sprite2.height):  # s1 is above s2
        return False
    if sprite2.y > (sprite1.y + sprite1.height):  # s1 is below s2
        return False
    return True

def update(dt):
    #update wall positions
    global walls, main_batch, player_snake, score, level
    if player_snake:
        to_remove = []
        for w in walls:
            w.x -= speed * dt
            if w.x < -w.width:
                to_remove.append(w)

        for w in to_remove:
            walls.remove(w)
            w.delete()

    #remove score
        score += len(to_remove)//2
        score_label.text = "Score: %d" % score

        to_remove = []
        for f in food:
            f.x -= speed * dt
            if f.x < -f.width:
                to_remove.append(f)

        for f in to_remove:
            food.remove(f)
            f.delete()

    # update snake positions and velocities
    for i,t in enumerate(snake_tail):
        t.vel_y -= gravity
        t.y += t.vel_y
        # make new velocity to chase next part of snake
        if player_snake:
            if i == 0 :
                t.vel_y = (player_snake.y - t.y) / (greensquare_image.width / speed *120.0)
            else:
                t.vel_y = (snake_tail[i-1].y - t.y) / (greensquare_image.width / speed *120.0)


    #update player position
    if player_snake:
        #handle food collision
        to_remove = []
        for f in food:
            if collides_with(player_snake, f):
                # increase snake size:
                tail_piece = pyglet.sprite.Sprite(img=greensquare_image, x=player_snake.x,
                                                    y=player_snake.y, batch=main_batch)
                snake_tail.insert(0,tail_piece)
                tail_piece.vel_y = player_snake.vel_y
                player_snake.x += player_snake.width
                player_snake.y = f.y
                f.delete()
                to_remove.append(f)

        for f in to_remove:
            food.remove(f)
            level += 1
            level_label.text = "LEVEL %d" % level



        if player_snake.y > game_window.height:
            player_snake.vel_y = 0

        player_snake.vel_y = max(-max_fall_vel,player_snake.vel_y - gravity)
        player_snake.y += player_snake.vel_y

        if player_snake.y < 0:

            tail_piece = pyglet.sprite.Sprite(img=greensquare_image, x=player_snake.x,
                                              y=player_snake.y, batch=main_batch)
            snake_tail.insert(0, tail_piece)
            player_snake.delete()
            player_snake = None
            pyglet.clock.unschedule(generateWallAndFood)
            level_label.text = "You died! Click to Restart"

            for t in snake_tail:
                t.rotation = random.randrange(90)
                t.vel_y = random.randint(jump_vel, jump_vel * 2)
            return


        #check for collisions
        for w in walls:
            if collides_with(player_snake, w):
                tail_piece = pyglet.sprite.Sprite(img=greensquare_image, x=player_snake.x,
                                                  y=player_snake.y, batch=main_batch)
                snake_tail.insert(0, tail_piece)
                player_snake.delete()
                player_snake = None
                pyglet.clock.unschedule(generateWallAndFood)
                level_label.text = "You died! Click to Restart"

                for t in snake_tail:
                    t.rotation = random.randrange(90)
                    t.vel_y = random.randint(jump_vel, jump_vel*2)




@game_window.event
def on_draw():
    game_window.clear()

    #draw things

    main_batch.draw()
    level_label.draw()
    score_label.draw()


@game_window.event
def on_key_press(symbol, modifiers):
    global player_snake, snake_tail, score, label, speed, walls, food, level
    if player_snake:
        # Jump
        if player_snake.vel_y <= min_fall_vel_to_jump:
            player_snake.vel_y = jump_vel

@game_window.event
def on_mouse_press(x, y, button, modifiers):
    global player_snake, snake_tail, walls, food, speed
    if not player_snake:
        # restart, should make function
        level = 1
        level_label.text = "LEVEL %d" % level

        score = 0
        score_label.text = "Score: %d" % score
        player_snake = pyglet.sprite.Sprite(img=greensquare_image, x = greensquare_image.width, y=game_window.height//2, batch=main_batch)
        player_snake.vel_y = jump_vel
        for t in snake_tail:
            t.delete()
        snake_tail = []

        for w in walls:
            w.delete()
        walls = []
        for f in food:
            f.delete()
        food = []

        speed = initial_speed
        pyglet.clock.schedule_once(generateWallAndFood, wall_interval)




def generateWallAndFood(dt):
    # Should check for game to continue
    if player_snake:

        lower_opening_y = makeWallPair(wall_opening, batch=main_batch)
        if score % food_freq == food_freq - 1:
            food_y = lower_opening_y + wall_opening/2 - greensquare_image.height/2
            f = pyglet.sprite.Sprite(img=greensquare_image, x=game_window.width + lowerwall_image.width//2 - greensquare_image.width//2,
                                              y=food_y, batch=main_batch)
            food.append(f)

            pyglet.clock.schedule_once(generateWallAndFood, wall_interval)


if __name__ == '__main__':
#    pyglet.clock.schedule_once(generateWallAndFood, wall_interval)
    pyglet.clock.schedule_interval(update, 1/120.0)
    pyglet.app.run()