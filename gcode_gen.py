import numpy
import cv2
import sys

def __preprocess(image, out_file, hsize, pixel_size_mm):
        # properly type these
        hsize = float(hsize)
        pixel_size_mm = float(pixel_size_mm)

        # dims
        y_size_input = image.shape[0]
        x_size_input = image.shape[1]

        # scale calculation 
        x_size_output = hsize/pixel_size_mm
        scale = x_size_output/x_size_input

        image = cv2.resize(image, (int(scale*x_size_input), int(scale*y_size_input)))
        
        y_size_output = image.shape[0]
        x_size_output = image.shape[1]
        # binary array, 1 for black
        img = numpy.rint(numpy.multiply(image, 1/255))
        img = numpy.subtract(1,img)

        #preview
        img_out=numpy.empty((x_size_output,y_size_output))
        img_out=numpy.rint(numpy.multiply(img, 255))
        img_out=numpy.subtract(255,img_out)
        img_out = img_out.astype(numpy.uint8)
        cv2.imwrite(out_file + "_Preview.png",img_out)
        
        img=numpy.flip(img,0)
        return img, y_size_output, x_size_output
    
def create_abs_gcode(image, out_file, hsize, pixel_size_mm):
    with open(out_file+"_Absolute.nc", 'w+') as f:

        img, y_size_output, x_size_output = __preprocess(image, out_file, hsize, pixel_size_mm)
        
        #allow user to change these in the future
        f.write("F500\n")
        f.write("G90\n")
        for y in range(y_size_output):
            # track the previous pixel color
            prev = 0
        
            if 1-y%2:
                for x in range(x_size_output):
                    # first pixel is black
                    if (x == 0  and img[y][x] == 1):
                        f.write("G0 X"+str(round(x*pixel_size_mm,4))+" Y" + str(round(y*pixel_size_mm,4))+"\n")                                                                                                              
                        f.write("G0 Z"+str(int(img[y][x]*5))+"\n")                                                                     
                        prev = int(img[y][x])
                    # last pixel
                    elif x==(x_size_output-1):
                        # write to here
                        if (prev==1):
                            f.write("G1 X"+str(round((x)*pixel_size_mm,4))+" Y" + str(round(y*pixel_size_mm,4))+"\n")      
                        prev=0
                    # we reach a different pixel
                    elif (prev != img[y][x]):
                        # start draw
                        if (prev==0): 
                            f.write("G0 X"+str(round((x-1)*pixel_size_mm,4))+" Y" + str(round(y*pixel_size_mm,4))+"\n")      
                            f.write("G0 Z"+str(int(img[y][x])*5)+"\n") 
                            prev = int(img[y][x])
                        # stop drawing
                        if(prev != 0):
                            f.write("G1 X"+str(round((x-1)*pixel_size_mm,4))+" Y" + str(round(y*pixel_size_mm,4))+"\n")      
                            f.write("G0 Z"+str(int(img[y][x])*5)+"\n")  
                            prev = int(img[y][x])
            else:
                # do same as above, but in reverse
                for x in reversed(range(x_size_output)):
                    if (x == x_size_output-1  and img[y][x] != 0): 
                        f.write("G0 X"+str(round(x*pixel_size_mm,4))+" Y" + str(round(y*pixel_size_mm,4))+"\n")                                                                                                              
                        f.write("G0 Z"+str(int(img[y][x])*5)+"\n")                                                                     
                        prev = int(img[y][x])
                    elif x==0:
                        if (prev==1):
                            f.write("G1 X"+str(round((x)*pixel_size_mm,4))+" Y" + str(round(y*pixel_size_mm,4))+"\n")      
                        prev=0
                    elif (prev != img[y][x]):
                        if (prev==0):
                            f.write("G0 X"+str(round((x)*pixel_size_mm,4))+" Y" + str(round(y*pixel_size_mm,4))+"\n")      
                            f.write("G0 Z"+str(int(img[y][x])*5)+"\n")                                                                     
                            prev = int(img[y][x])
                        if(prev != 0):
                            f.write("G1 X"+str(round((x)*pixel_size_mm,4))+" Y" + str(round(y*pixel_size_mm,4))+"\n")      
                            f.write("G0 Z"+str(int(img[y][x])*5)+"\n")                                                                     
                            prev = int(img[y][x])
        f.close()



def create_rel_gcode(image, out_path, hsize, pixel_size_mm):
    with open(out_path + '_Relative.nc', 'w+') as f:
        img, y_size_output, x_size_output = __preprocess(image, out_path, hsize, pixel_size_mm)

        #hard coded feed rate of 500 and relative positioning, allow option in GUI for future
        f.write("F500\n")
        f.write("G91\n")
        
        for y in range(y_size_output):
            prev = 0
            dist = 0
            #alternate the sweep
            if 1-y%2:
                for x in range(x_size_output):
                    #prev = first point
                    if(x==0 and y==0):
                        prev = img[y][x]
                        dist = 0
                    #move down if necessary
                    elif(x==0):
                        f.write("G1 X0 Y"+str(round(pixel_size_mm,4))+" Z0 \n")
                        prev = img[y][x]
                        dist = 0
                    #current point is different, and previous is black
                    if(img[y][x]!=prev and prev):
                        f.write("G0 X0 Y0 Z-5\n")
                        f.write("G1 X"+str(round(-1*dist*pixel_size_mm,4))+" Y0 Z0\n")
                        f.write("G0 X0 Y0 Z5\n")
                        dist = 0
                    #current point is different, and previous is white
                    elif(img[y][x]!=prev and not prev):
                        f.write("G1 X"+str(round(-1*dist*pixel_size_mm,4))+" Y0 Z0\n")
                        dist = 0
                    #eol
                    if(x==(x_size_output)-1):
                        #if black line to finish
                        if(prev and dist):
                            f.write("G0 Z-5\n")
                            f.write("G1 X"+str(round(-1*dist*pixel_size_mm,4))+" Y0 Z0\n")
                            f.write("G0 Z5\n")
                            dist = 0
                        #if white line to finish
                        elif(dist):
                            f.write("G1 X"+str(round(-1*dist*pixel_size_mm,4))+" Y0 Z0\n")
                            dist = 0
                    dist+=1
                    prev = img[y][x]
            else:
                for x in reversed(range(x_size_output)):
                    #prev = first point
                    if(x==x_size_output-1):
                        prev = img[y][x]
                        dist = 0
                        f.write("G1 X0 Y"+str(round(pixel_size_mm,4))+" Z0\n")
                    #current point is different, and previous is black
                    if(img[y][x]!=prev and prev):
                        f.write("G0 Z-5\n")
                        f.write("G1 X"+str(round(dist*pixel_size_mm,4))+" Y0 Z0\n")
                        f.write("G0 Z5\n")
                        dist = 0
                    #current point is different, and previous is white
                    elif(img[y][x]!=prev and not prev):
                        f.write("G1 X"+str(round(dist*pixel_size_mm,4))+" Y0 Z0\n")
                        dist = 0
                    #eol
                    if(x==0):
                        #if black line to finish
                        if(prev and dist):
                            f.write("G0 Z-5\n")
                            f.write("G1 X"+str(round(dist*pixel_size_mm,4))+"\n")
                            f.write("G0 Z5\n")
                            dist = 0
                        #if white line to finish
                        elif(dist):
                            f.write("G1 X"+str(round(dist*pixel_size_mm,4))+"\n")
                            dist = 0
                    dist+=1
                    prev = img[y][x]
        f.close()

def generate(image_path, out_name, threshold=127, hsize = 100, pixel_size_mm = 0.5):
    try:
        # grayscale
        image = cv2.imread(image_path, 0)
        (thresh, image) = cv2.threshold(image, threshold, 255, cv2.THRESH_BINARY)
        create_rel_gcode(image, out_name, hsize, pixel_size_mm)
        create_abs_gcode(image, out_name, hsize, pixel_size_mm)
    except:
        print("Error reading image!")
        return

if __name__ == "__main__":
    if(len(sys.argv) == 3):
        generate(sys.argv[1], sys.argv[2])
    elif(len(sys.argv) == 4):
        generate(sys.argv[1], sys.argv[2], sys.argv[3])
    elif(len(sys.argv) == 5):
        generate(sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4])
    elif(len(sys.argv) == 6):
        generate(sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4], sys.argv[5])
    else:
        print("Usage: python gcode_gen.py image_path out_name")
        print("Additional args: threshold horizontal_size pixel_size_mm")