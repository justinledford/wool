from PIL import Image, ImageFont, ImageDraw

ROW_SIZE = 50
SPACE_SIZE = 10


img = Image.new('RGB', (500, 500), 'white')

draw = ImageDraw.Draw(img)
draw.rectangle(((50, 50), (100, 100)), fill='#3AAFD9')
draw.rectangle(((110, 50), (160, 100)), fill='#BD44B3')
draw.rectangle(((170, 50), (220, 100)), fill='#F8C627')
draw.rectangle(((230, 50), (280, 100)), fill='#8E8E86')
draw.text((25, 70), '1', fill='black')

draw.rectangle(((50, 150), (100, 200)), fill='#ED8DAC')
draw.rectangle(((110, 150), (160, 200)), fill='#35399D')
draw.rectangle(((170, 150), (220, 200)), fill='#70B919')
draw.rectangle(((230, 150), (280, 200)), fill='#A12722')
draw.text((25, 170), '2', fill='black')

img.save('test.jpg', 'JPEG', quality=95)
