from PIL import Image, ImageDraw, ImageFont


# coor_list = [
#     (968,1096), (772, 1096), (572, 1050), (474, 1096), (278, 1096), (180, 1096), \
#     (35, 964), (70, 866), (35, 768), (35, 670), (100, 572), (35, 474), (35, 278), (35, 180), \
#     (20, 20), (180, 52), (376, 52), (474, 52), (572, 100), (670, 52), (772, 52), (870, 100), (968, 52), \
#     (1074, 15), (1090, 180), (1090, 278), (1090, 474), (1060, 572), (1090, 768), (1090, 964)]
def create_a_map(name_list, topic):
    coor_list = [(474, 1096), (278, 1096), (180, 1096), (35, 964), (35, 768), (35, 670), (35, 474), (35, 278),
                 (35, 180), (180, 52), (376, 52), (474, 52), (670, 52), (772, 52),
                 (968, 52), (1090, 180), (1090, 278), (1090, 474), (1090, 768), (1090, 964), (968, 1096), (772, 1096),
                 (70, 866), (870, 100), (572, 1050), (100, 572), (572, 100), (1060, 572), (1074, 15), (20, 20)]

    address_name_list = [name.replace(' ', '\n') for name in name_list][1:]
    base_map_path = "./images/map_base.jpg"
    base_map = Image.open(base_map_path).convert("RGBA")
    topic = topic.replace(' ', '_')

    # make a blank image for the text, initialized to transparent text color
    text = Image.new("RGBA", base_map.size, (255, 255, 255, 0))

    # get a font
    my_font = ImageFont.truetype("/Library/Fonts/Arial Unicode.ttf", 15)

    # get a drawing content
    map_text = ImageDraw.Draw(text)

    for cola, address_name in zip(coor_list, address_name_list):  # address name list need to content \n
        map_text.multiline_text(cola, address_name, font=my_font, fill=(0, 0, 0))

    # combine the two pics
    out = Image.alpha_composite(base_map, text)
    # out.show()
    # save the new map
    save_path = f'./images/{topic}.png'
    out.save(save_path)
    return save_path

