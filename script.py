import mdl
from display import *
from matrix import *
from draw import *

"""======== first_pass( commands ) ==========

  Checks the commands array for any animation commands
  (frames, basename, vary)

  Should set num_frames and basename if the frames
  or basename commands are present

  If vary is found, but frames is not, the entire
  program should exit.

  If frames is found, but basename is not, set name
  to some default value, and print out a message
  with the name being used.
  ==================== """
def first_pass( commands ):

    name = 'default'
    num_frames = 1

    frames_pres = False
    vary_pres = False

    for command in commands:
        #print command
        c = command['op']
        args = command['args']
        
        if c == "frames":
            num_frames = int(args[0])
            frames_pres = True
        elif c == "vary":
            vary_pres = True
        elif c == "basename":
            name = args[0]
            #print(name)

    #print("Name "+name+" is being used.")
    if vary_pres and not frames_pres:
        sys.exit()

    #print(num_frames)
    return (name, num_frames)

"""======== second_pass( commands ) ==========

  In order to set the knobs for animation, we need to keep
  a separate value for each knob for each frame. We can do
  this by using an array of dictionaries. Each array index
  will correspond to a frame (eg. knobs[0] would be the first
  frame, knobs[2] would be the 3rd frame and so on).

  Each index should contain a dictionary of knob values, each
  key will be a knob name, and each value will be the knob's
  value for that frame.

  Go through the command array, and when you find vary, go
  from knobs[0] to knobs[frames-1] and add (or modify) the
  dictionary corresponding to the given knob with the
  appropriate value.
  ===================="""
def second_pass( commands, num_frames ):
    frames = [ {} for i in range(num_frames) ]

    for command in commands:
        if command["op"] == "vary":
            for i in range( int(command["args"][0]), int(command["args"][1]) + 1 ):
                frames[i][ command["knob"] ] = command["args"][2] + \
                (command["args"][3] - command["args"][2]) * (i - command["args"][0]) \
                / (command["args"][1] - command["args"][0])


    print(frames)
    return frames


def run(filename):
    """
    This function runs an mdl script
    """
    p = mdl.parseFile(filename)

    if p:
        (commands, symbols) = p
    else:
        print "Parsing failed."
        return

    view = [0,
            0,
            1];
    ambient = [50,
               50,
               50]
    light = [[0.5,
               0.75,
              1],
             [255,
              255,
              255]]

    color = [0, 0, 0]
    symbols['.white'] = ['constants',
                         {'red': [0.2, 0.5, 0.5],
                          'green': [0.2, 0.5, 0.5],
                          'blue': [0.2, 0.5, 0.5]}]
    reflect = '.white'

    (name, num_frames) = first_pass(commands)
    frames = second_pass(commands, num_frames)

    for frm in range(num_frames):
        tmp = new_matrix()
        ident( tmp )

        stack = [ [x[:] for x in tmp] ]
        screen = new_screen()
        zbuffer = new_zbuffer()
        tmp = []
        step_3d = 100
        consts = ''
        coords = []
        coords1 = []

        for each in frames[frm]:
            symbols[each] = frames[frm][each]
        
        for command in commands:

            print command
            c = command['op']
            args = command['args']
            knob_value = 1
            
            if c == 'box':
                if command['constants']:
                    reflect = command['constants']
                add_box(tmp,
                        args[0], args[1], args[2],
                        args[3], args[4], args[5])
                matrix_mult( stack[-1], tmp )
                draw_polygons(tmp, screen, zbuffer, view, ambient, light, symbols, reflect)
                tmp = []
                reflect = '.white'
                
            elif c == 'sphere':
                if command['constants']:
                    reflect = command['constants']
                add_sphere(tmp,
                        args[0], args[1], args[2], args[3], step_3d)
                matrix_mult( stack[-1], tmp )
                draw_polygons(tmp, screen, zbuffer, view, ambient, light, symbols, reflect)
                tmp = []
                reflect = '.white'
                
            elif c == 'torus':
                tmp = []
                if command['constants']:
                    reflect = command['constants']
                add_torus(tmp,
                              args[0], args[1], args[2], args[3], args[4], step_3d)
                matrix_mult( stack[-1], tmp )
                draw_polygons(tmp, screen, zbuffer, view, ambient, light, symbols, reflect)
                tmp = []
                reflect = '.white'
                
            elif c == 'line':
                add_edge(tmp,
                    args[0], args[1], args[2], args[3], args[4], args[5])
                matrix_mult( stack[-1], tmp )
                draw_lines(tmp, screen, zbuffer, color)
                tmp = []
                
            elif c == 'move':
                arg_0 = args[0]
                arg_1 = args[1]
                arg_2 = args[2]

                if command["knob"]:
                    arg_0 *= symbols[ command["knob"] ] #frames[frm][ command["knob"] ]
                    arg_1 *= symbols[ command["knob"] ] #frames[frm][ command["knob"] ]
                    arg_2 *= symbols[ command["knob"] ] #frames[frm][ command["knob"] ]

                print("\nmove variables: {}, {}, {}\n".format(arg_0, arg_1, arg_2))
                    
                tmp = make_translate(arg_0, arg_1, arg_2)

                matrix_mult(stack[-1], tmp)
                stack[-1] = [x[:] for x in tmp]
                tmp = []
                
            elif c == 'scale':
                arg_0 = args[0]
                arg_1 = args[1]
                arg_2 = args[2]

                if command["knob"]:
                    arg_0 *= symbols[ command["knob"] ] #frames[frm][ command["knob"] ]
                    arg_1 *= symbols[ command["knob"] ] #frames[frm][ command["knob"] ]
                    arg_2 *= symbols[ command["knob"] ] #frames[frm][ command["knob"] ]

                print("\nscale variables: {}, {}, {}\n".format(arg_0, arg_1, arg_2))
                    
                tmp = make_scale(arg_0, arg_1, arg_2)
                
                matrix_mult(stack[-1], tmp)
                stack[-1] = [x[:] for x in tmp]
                tmp = []
                
            elif c == 'rotate':
                arg_1 = args[1]

                if command["knob"]:
                    arg_1 *= symbols[ command["knob"] ] #frames[frm][ command["knob"] ]                   

                print("{}".format(arg_1))
                
                theta = arg_1 * (math.pi/180)
                if args[0] == 'x':
                    tmp = make_rotX(theta)
                elif args[0] == 'y':
                    tmp = make_rotY(theta)
                else:
                    tmp = make_rotZ(theta)
                matrix_mult( stack[-1], tmp )
                stack[-1] = [ x[:] for x in tmp]
                tmp = []
                
            elif c == 'push':
                stack.append([x[:] for x in stack[-1]] )
                
            elif c == 'pop':
                stack.pop()
                
            elif c == 'display':
                display(screen)
                
            elif c == 'save':
                save_extension(screen, args[0])
            save_extension(screen, "anim/" + name + "%03d"%frm)
            # end operation loop
