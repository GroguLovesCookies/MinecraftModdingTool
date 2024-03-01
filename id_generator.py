import random


def generate_random_id():
    final = ""
    seed = int(random.random() * 104324242)
    multiplier = seed % 19
    target_root = 3.14 * multiplier
    target_value = target_root * target_root
    final_pre_scramble = str(seed * target_value)
    dot_index = final_pre_scramble.index(".")
    print(final_pre_scramble, dot_index)
    final_pre_scramble = final_pre_scramble.replace(".", "0")
    
    for i, char in enumerate(final_pre_scramble):
        offset = int(char) + i
        final += str(offset) + "."
    final += str(dot_index)

    return final


def validate_id(identification):
    end_seed = ""
    sections = identification.split(".")
    dot_index = 0
    for i, section in enumerate(sections):
        if i < len(sections) - 1:
            processed_digit = int(section) - i
            end_seed += str(processed_digit)
        else:
            dot_index = int(section)
    
    split_seed = list(end_seed)
    split_seed[dot_index] = '.'
    end_seed = "".join(split_seed)
    try:
        end_seed = float(end_seed)
        result = end_seed/(3.14*3.14)
    except ValueError:
        return False
    return abs(int(result) - result) < 0.001
