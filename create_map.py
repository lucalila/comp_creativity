from PIL import Image, ImageDraw, ImageFont, UnidentifiedImageError
from google_image_api import insert_a_pic
#
# name_list = ['GO',
#              'Mr. Nobody Street',
#              'Deckard Shaw Drive',
#              'Han Drive',
#              'Sean Boswell Lane',
#              'Elena Boulevard',
#              'Hector Road',
#              'Owen Shaw Drive',
#              'Safar Road',
#              'Jack Lane',
#              'Samantha Hobbs Alley',
#              'Letty Fan Park',
#              'Female Racer Park',
#              'Race Starter Lane',
#              'Hot Teacher Drive',
#              'Doctor Park',
#              'Merc Tech Road',
#              'Weapons Tech Lane',
#              'Dominic Toretto Avenue',
#              "Brian O'Conner Avenue",
#              'Kiet Drive',
#              'Kara Drive',
#              'Walker',
#              'Los Angeles',
#              'Letty Station',
#              'Roman Station',
#              "Tej (as Chris 'Ludacris' Bridges) Station",
#              'Mia Station',
#              'Walker',
#              'Abu Dhabi']


# coor_list = [
#     (968,1096), (772, 1096), (572, 1050), (474, 1096), (278, 1096), (180, 1096), \
#     (35, 964), (70, 866), (35, 768), (35, 670), (100, 572), (35, 474), (35, 278), (35, 180), \
#     (20, 20), (180, 52), (376, 52), (474, 52), (572, 100), (670, 52), (772, 52), (870, 100), (968, 52), \
#     (1074, 15), (1090, 180), (1090, 278), (1090, 474), (1060, 572), (1090, 768), (1090, 964)]

def create_a_map(name_list, topic):
    coor_list = [(465, 1096), (270, 1096), (170, 1096), (30, 955), (30, 768), (30, 670), (30, 465), (30, 268),
                 (30, 170), (170, 30), (365, 30), (465, 30), (660, 30), (762, 30),
                 (958, 30), (1090, 165), (1090, 265), (1090, 455), (1090, 763), (1090, 960), (958, 1096), (755, 1096),
                 (63, 855), (860, 105), (567, 1040), (100, 572), (567, 100), (1050, 572), (1094, 5), (15, 10)]

    address_name_list = [name.replace(' ', '\n') for name in name_list][1:]
    base_map_path = "./images/map_base.jpg"
    base_map = Image.open(base_map_path).convert("RGBA")

    # make a blank image for the text, initialized to transparent text color
    text = Image.new("RGBA", base_map.size, (255, 255, 255, 0))

    # get a font
    address_font = ImageFont.truetype("./fonts/address.otf", 22)
    dimension_font = ImageFont.truetype("./fonts/text.otf", 40)

    # get a drawing content
    map_text = ImageDraw.Draw(text)

    for cola, address_name in zip(coor_list, address_name_list):  # address name list need to content \n
        map_text.multiline_text(cola, address_name, font=address_font, fill=(0, 0, 0))
    map_text.multiline_text((185, 544), f'Current Dimension: {topic}', font=dimension_font, fill=(0, 0, 0))

    try:
        add_pic_path = insert_a_pic(topic)
        add_pic = Image.open(add_pic_path).convert('RGBA')
        add_pic = add_pic.resize((840, 430))

        # combine the two pics
        out = Image.alpha_composite(base_map, text)
        out.paste(add_pic, (192, 600))
        # save the new map

    except UnidentifiedImageError:
        print('Sorry we have not found the right pic for this movie.')
        out = Image.alpha_composite(base_map, text)

    out = out.resize((750, 750))  # out.show()
    topic = topic.replace(' ', '_')
    save_path = f'./images/{topic}.png'
    out.save(save_path)
    return save_path


# create_a_map(name_list, 'the frozen')
