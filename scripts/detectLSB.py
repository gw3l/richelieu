#!/usr/bin/env python
# encoding: utf-8

import os
from PIL import Image
import argparse
 
def main(input, output):
  img = Image.open(input)
  data = list(img.getdata())
  newdata = list()
  for r,g,b in data:
    r = (r & 1) << 7
    g = (g & 1) << 7
    b = (b & 1) << 7
    newdata.append((r, g, b))

  newimg = Image.new(img.mode, img.size)
  newimg.putdata(newdata)
  newimg.save(output)
 
if __name__ == '__main__':

  parser = argparse.ArgumentParser(description='Simple steg detect, Thx Mortis :)')
  parser.add_argument("-i", action="store", dest="input", help="input file", required=True)
  parser.add_argument("-o", action="store", dest="output", help="output file", required=True)
  command = parser.parse_args()
main(command.input, command.output)

