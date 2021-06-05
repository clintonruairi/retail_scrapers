size_colours = []
        size_colour_pattern = r'"v3": ".+"'
        var_size_colours = re.findall(size_colour_pattern, variant_text)
        for item in var_size_colours:
            item = item.replace('"v3": "', '')
            item = item.replace('"', '')
            size_colours.append(item[::-1])
        new_sizes = []
        new_colors = []
        for size in size_colours:
            multi_backslashes = [i.start() for i in re.finditer('/', size)]
            if len(multi_backslashes) > 1:
                size = size[:multi_backslashes[1]]
                size_pattern = r'.+ \/'
                size_result = re.search(size_pattern, size)
                new_size = size_result.group().replace(' /', '')
                colour_pattern = r'/ .+'
                colour_result = re.search(colour_pattern, size)
                color = colour_result.group().replace('/ ', '')
                color = color.strip()
                new_sizes.append(new_size)
                new_colors.append(color)
            else:
                size_pattern = r'.+ \/'
                size_result = re.search(size_pattern, size)
                new_size = size_result.group().replace(' /', '')
                colour_pattern = r'/ .+'
                colour_result = re.search(colour_pattern, size)
                color = colour_result.group().replace('/ ', '')
                color = color.strip()
                new_sizes.append(new_size)
                new_colors.append(color)
        count = 0