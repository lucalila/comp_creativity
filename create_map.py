from PIL import Image, ImageDraw, ImageFont

coor_list = [(94,64), (210, 64)]
address_name_list = ['Start', 'Chance']

base_map = Image.open("./map/map_structure.jpeg").convert("RGBA")
# print(map_basic.format, map_basic.size)

# make a blank image for the text, initialized to transparent text color
text = Image.new("RGBA", base_map.size, (255, 255, 255, 0))

# get a font
my_font = ImageFont.truetype("/Library/Fonts/Arial Unicode.ttf", 18)

# get a drawing content
map_text = ImageDraw.Draw(text)

for cola, address_name in zip(coor_list, address_name_list):   # address name list need to content \n
    map_text.multiline_text(cola, address_name, font=my_font, fill=(0,0,0))

#combine the two pics
out = Image.alpha_composite(base_map, text)

out.show()





