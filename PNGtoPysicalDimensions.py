import numpy as np
import matplotlib.pyplot as plt
import cv2
import argparse
import sys

# Take parameters from LCD physical dimensions
CNF_LCD_W_mm=412.0
CNF_LCD_H_mm=233.0
CNF_LCD_W_pixels=1360
CNF_LCD_H_pixels=768

# Take parameters from paper size from the CAD Tool
# Assuming A4 paper size
CNF_PNG_W_mm=297.0
CNF_PNG_H_mm=210.0

class PhysicalImageDimensions(object):
    def __init__(self, w_pixels: int, h_pixels: int, w_mm : float, h_mm: float, rescale_factor : int = 1):
        self.__w_pixels = w_pixels
        self.__h_pixels = h_pixels
        self.__w_mm = w_mm
        self.__h_mm = h_mm
        self.__rescale_factor = rescale_factor
    @property
    def w(self) -> int:
        return self.__w_pixels
    @property
    def h(self) -> int:
        return self.__h_pixels
    @property
    def w_mm(self) -> float:
        return self.__w_mm
    @property
    def h_mm(self) -> float:
        return self.__h_mm

    @property
    def shape(self) -> tuple:
        return (self.h * self.__rescale_factor ,self.w * self.__rescale_factor, 4)
    
    @property
    def physical_shape(self) -> tuple:
        return (self.h_mm,self.w_mm)
    
    @property
    def h_ppmm(self) -> int:
        """Pixels Per mm"""
        return self.h * self.__rescale_factor / self.h_mm
    
    @property
    def w_ppmm(self) -> int:
        """Pixels Per mm"""
        return self.w * self.__rescale_factor / self.w_mm

class PhysicalPictureFile(object):
    def __init__(self, path : str, w_mm : float, h_mm: float ) -> None:
        img = cv2.imread( path )
        self.__img = img
        h, w,_ = img.shape
        self.__physical_image = PhysicalImageDimensions(
            w_pixels=w,
            h_pixels=h,
            w_mm=w_mm,
            h_mm=h_mm
        )
    @property
    def physical_dimensions(self) -> PhysicalImageDimensions:
        return self.__physical_image

    @property
    def img(self):
        return self.__img

    @property
    def shape(self) -> tuple:
        return self.__img.shape
    
    @property
    def channels(self) -> int:
        return self.__img.shape[2]

    @property
    def physical_shape(self) -> tuple:
        return (self.__physical_image.h_mm, self.__physical_image.w_mm)

def getArgParser():
    parser = None
    if( parser is None ):
        if( sys.version_info.minor >= 9):
            parser = argparse.ArgumentParser(description='Map file Analyzer',exit_on_error=True)
        else:
            parser = argparse.ArgumentParser(description='Map file Analyzer')
        parser.add_argument("--png", nargs=1, required=False, help="PNG image" , dest="png_file")
        parser.add_argument("-o","--output", nargs=1, required=True, help="PNG output file", dest="output_file")
    return parser

def main():
    args = getArgParser().parse_args( sys.argv[1:] )
    png_file = args.png_file[0]
    output_png_file = args.output_file[0]

    # Load an image with the paper size parameters
    png = PhysicalPictureFile( png_file, w_mm=CNF_PNG_W_mm, h_mm=CNF_PNG_H_mm )

    # Load LCD physical dimensions
    lcd = PhysicalImageDimensions( w_pixels=CNF_LCD_W_pixels,
                                  h_pixels=CNF_LCD_H_pixels,
                                  w_mm=CNF_LCD_W_mm,
                                  h_mm=CNF_LCD_H_mm,
                                  rescale_factor=1 )

    # Verify that physical dimensions are right
    if( (png.physical_dimensions.h_mm > lcd.h_mm) or (png.physical_dimensions.w_mm > lcd.w_mm) ):
        raise Exception(f"Picture physical size is greater than the LCD: LCD[{lcd.physical_shape} mm] picture[{png.physical_shape} mm]")

    # Convert LCD physical dimensions to pixels using PNG density (avoid resize to preserve resolution as high as possible)
    lcd_h_pixels = int( lcd.h_mm * png.physical_dimensions.h_ppmm )
    lcd_w_pixels = int( lcd.w_mm * png.physical_dimensions.w_ppmm )

    # Take the shape of the input image
    (h,w,c) = png.img.shape

    # Add Horizontal Pixels to resize width
    lcd_frame_buffer = cv2.hconcat( [ png.img, 255 * np.ones( shape=( h, lcd_w_pixels - w, c ), dtype=np.uint8 ) ] )

    # Add Vertical Pixels to resize height
    lcd_frame_buffer = cv2.vconcat( [ lcd_frame_buffer, 255* np.ones( shape=( lcd_h_pixels - h, lcd_w_pixels, c ), dtype=np.uint8 ) ] )

    # Save new PNG file
    cv2.imwrite( output_png_file, lcd_frame_buffer )

if __name__ == "__main__":
    main()
