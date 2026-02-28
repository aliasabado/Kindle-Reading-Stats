from PIL import Image, ImageDraw, ImageFont
#FFF1EB

# Create a blank image
canvas_width, canvas_height = 400, 500
image = Image.new('RGB', (canvas_width, canvas_height), color='#FFF1EB')
draw = ImageDraw.Draw(image)

# Load fonts
try:
    header_font = ImageFont.truetype("times.ttf", 36)  
    text_font = ImageFont.truetype("timesbd.ttf", 20)   
except IOError:
    header_font = ImageFont.load_default()
    text_font = ImageFont.load_default()

# Data
total_time = "1200 minutes"
days = "15"
average_per_day = "80"
page_flips = "500"

# Lines to draw (header, text)
lines = [
    ("Total Reading Time", f"You have spent {total_time} reading in total."),
    ("Active Reading Days", f"You engaged with your Kindle on {days} distinct days."),
    ("Average Daily Reading Time", f"That is an average of {average_per_day} minutes per day."),
    ("Pages Turned", f"You flipped approximately {page_flips} pages during this period."),
]

# Function to wrap text within a max width
def wrap_text(text, font, max_width):
    words = text.split()
    lines = []
    current_line = ""
    for word in words:
        test_line = f"{current_line} {word}".strip()
        bbox = draw.textbbox((0, 0), test_line, font=font)
        line_width = bbox[2] - bbox[0]
        if line_width <= max_width:
            current_line = test_line
        else:
            lines.append(current_line)
            current_line = word
    if current_line:
        lines.append(current_line)
    return lines

# Draw lines
y = 20  # starting y-coordinate
spacing_header = 10
spacing_text = 10

# Function to draw text with variable highlighting
def draw_colored_text(x, y, text, variable_color="red", normal_color="darkblue"):
    words = text.split()
    current_x = x
    for word in words:
        # Determine if word is a variable (numbers or contains digits)
        color = variable_color if any(char.isdigit() for char in word) else normal_color
        bbox = draw.textbbox((0,0), word + " ", font=text_font)
        draw.text((current_x, y), word + " ", fill=color, font=text_font)
        current_x += bbox[2] - bbox[0]
    return y + bbox[3] - bbox[1]

for header, text in lines:
    # Draw header centered
    bbox = draw.textbbox((0,0), header, font=header_font)
    header_width = bbox[2] - bbox[0]
    draw.text(((canvas_width - header_width)/2, y), header, fill="black", font=header_font)
    y += bbox[3] - bbox[1] + spacing_header

    # Wrap text
    wrapped_lines = wrap_text(text, text_font, canvas_width - 40)  # 20px padding each side
    for line in wrapped_lines:
        # Draw each line centered with variable highlighting
        bbox = draw.textbbox((0,0), line, font=text_font)
        line_width = bbox[2] - bbox[0]
        y = draw_colored_text((canvas_width - line_width)/2, y, line, variable_color="red", normal_color="darkblue")
        y += spacing_text

    y += 10  # extra spacing between sections

# Save image
image.save("reading_summary_colored.png")
print("Image saved as reading_summary_colored.png")