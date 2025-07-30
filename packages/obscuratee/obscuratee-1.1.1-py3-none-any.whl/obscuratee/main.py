from multiprocessing.spawn import old_main_modules
import random
import textwrap
import re

facts = [
        "Manatees communicate exclusively through underwater jazz.",
        "A group of manatees is called a 'blorb'.",
        "Manatees have never paid taxes — legally.",
        "Every manatee is born knowing three knock-knock jokes.",
        "Manatees were the first mammals to master the moonwalk.",
        "In ancient times, manatees were considered sea wizards.",
        "Manatees can hold their breath longer than your last relationship.",
        "All manatees know the secret ending to Lost.",
        "If you whisper 'vibes' into the ocean, a manatee will hear you.",
        "Manatees sleep exactly 23 minutes at a time. No more. No less.",
        "A manatee once ran for mayor in Florida. It won.",
        "Manatees don't float — the ocean just holds them gently.",
        "The original keyboard layout was made for manatee flippers.",
        "Manatees were the first creatures to discover lo-fi beats.",
        "Each manatee is born with a random Star Wars opinion.",
        "Manatees use sonar to find snacks and avoid responsibilities.",
        "There is at least one manatee with a PhD in art history.",
        "If a manatee blinks twice at you, it's challenging you to Mario Kart.",
        "Some manatees are secretly part of the USPS.",
        "A manatee once predicted the stock market crash of 2008.",
        "Manatees hate Mondays and it's been scientifically proven.",
        "The first manatee was coded in Assembly.",
        "Manatees don't sweat the small stuff. Or the big stuff. Or anything.",
        "There's a manatee somewhere that knows every lyric to Bohemian Rhapsody.",
        "Manatees are 80% water, 10% vibes, and 10% conspiracy theories.",
        "If you play ska underwater, manatees will skank with you.",
        "Manatees believe the moon landing was real — but faked.",
        "Each manatee gets one free wish per lifetime. They usually wish for lettuce.",
        "Manatees can detect sarcasm. They just don't react.",
        "Some manatees practice underwater parkour.",
        "A manatee invented the word 'blorbo' in 2011.",
        "There's a manatee somewhere with a podcast about soup.",
        "Manatees don't believe in time. Only snacks.",
        "All manatees share one single memory of a long-lost beach ball.",
        "A manatee once hacked into NASA using only flipper taps.",
        "The plural of manatee is 'chaos'.",
        "Manatees can legally run for office in three U.S. states.",
        "Most manatees follow at least one ASMR channel.",
        "Manatees breathe air but vibe in water.",
        "A manatee once beat Bobby Fischer in chess. The footage was lost.",
        "Manatees are banned from three buffets in Orlando.",
        "Every manatee secretly thinks it's an otter with depression.",
        "The default manatee mood is 'floating and judging you'.",
        "Manatees don't do taxes. They transcend them.",
        "Manatees don't sink or float. They simply exist.",
        "One manatee in the Gulf knows how to backflip. It won't teach the others.",
        "Some manatees can detect passive aggression.",
        "Manatees are emotionally immune to cringe.",
        "In 2004, a manatee won a hot dog eating contest. It wasn't pretty.",
        "Manatees once ran an underwater jazz club. It's now a Subway."
    ]


def make_bubble(text, width=40):
    wrapped = textwrap.wrap(text, width=width)
    top = "  " + "_" * (width + 2)
    mid = [f" | {line.ljust(width)} |" for line in wrapped]
    bottom = "  " + "-" * (width + 2)
    tail = ["         \\", "          \\"]
    return "\n".join([top, " /" + " " * (width + 2) + "\\"] + mid + [" \\" + "_" * (width + 2) + "/"] + tail)

def rainbowify(text):
    colors = [
        "\033[91m",  # Red
        "\033[93m",  # Yellow
        "\033[92m",  # Green
        "\033[96m",  # Cyan
        "\033[94m",  # Blue
        "\033[95m",  # Magenta
    ]
    reset = "\033[0m"
    result = ""
    for i, char in enumerate(text):
        color = colors[i % len(colors)]
        result += f"{color}{char}"
    return result + reset

def rainbowify_ansi(text):
    # Regex to match ANSI escape codes
    ansi_re = re.compile(r'(\x1b\[[0-9;]*m)')
    segments = ansi_re.split(text)
    result = ''
    for segment in segments:
        if ansi_re.match(segment):
            result += segment
        else:
            for char in segment:
                # Only color visible characters
                if char.strip() == '':
                    result += char
                else:
                    r = random.randint(0,255)
                    g = random.randint(0,255)
                    b = random.randint(0,255)
                    result += f'\x1b[38;2;{r};{g};{b}m{char}\x1b[0m'
    return result

def obscuratee_legacy(vibe=False):

    eyes = [
        " /  o   o  \\",
        " /  0   0  \\",
        " /  -   -  \\",
        " /  @   @  \\",
        " /  ◉   ◉  \\",
        " /  x   x  \\"
    ]

    noses = [
        "|    ^     |",
        "|    ~     |",
        "|    >     |",
        "|    .     |",
        "|    w     |",
        "|    ▽     |",
        "|    _     |"
    ]

    mouths = [
        " \\  ---   /",
        " \\  ___   /",
        " \\  ===   /",
        " \\  zzz   /",
        " \\  hehe  /"
    ]

    fact = random.choice(facts)
    bubble = make_bubble(fact)

    eye_line = random.choice(eyes)
    nose_line = random.choice(noses)
    mouth_line = random.choice(mouths)

    ascii_manatee_old = f"""
                            --=====+=====                             
                        ----------=======+===                        
                    :--=--:---=-=-=--==--=+=====                      
                ---:--------=--=--===--==========                    
            -------------=-======+=+* {eye_line}=-                   
            =-------=-----========++++#+++====:-====+                  
            ----------------==++=++=+=++++=+======-+++                  
        =-----------::----===++*=+++=======+{nose_line}=                 
        ----::::::::-:::---==++*#=#=--==++*+*{mouth_line}=                 
        =----::::::::-:::-=--==+*##+---==+******-===                 
        =----::::::::::::-++:--=+**#=--==+++**#%%*                  
        ==---:::--::::::=##%+-===++**#+++#***###                    
        +=+===-----------:+#%%%%%#######%%%**#                        
    =++++++++====----==--**+*#%%###   #%%%##                         
   +++++++++*****+++++++--*#%##       *%%%%%                          
   +++++++*******        -=#%%%       *%%%                            
    **********          -#%%%                                       
                        =%%                                               
"""

    if vibe:
        bubble = rainbowify(bubble)
        ascii_manatee_old = rainbowify(ascii_manatee_old)

    print(bubble)
    print(ascii_manatee_old)

def obscuratee(vibe=False):
    fact = random.choice(facts)
    bubble_lines = [
        "",  # Add an empty line before the bubble
        "                        \x1b[38;2;0;0;0m █████████████████████████████████████\x1b[0m",
        "                       \x1b[38;2;0;0;0m██\x1b[38;2;254;254;254m█████████████████████████████████████\x1b[38;2;0;0;0m██\x1b[0m",
        "                       \x1b[38;2;0;0;0m██\x1b[38;2;254;254;254m█████████████████████████████████████\x1b[38;2;0;0;0m██\x1b[0m",
        "                       \x1b[38;2;0;0;0m██\x1b[38;2;254;254;254m█████████████████████████████████████\x1b[38;2;0;0;0m██\x1b[0m",
        "                       \x1b[38;2;0;0;0m██\x1b[38;2;254;254;254m█████████████████████████████████████\x1b[38;2;0;0;0m██\x1b[0m",
        "                       \x1b[38;2;0;0;0m██\x1b[38;2;254;254;254m█████████████████████████████████████\x1b[38;2;0;0;0m██\x1b[0m",
        "                        \x1b[38;2;0;0;0m █████████████████████████████████████\x1b[0m",
        # Bubble tail (connects to manatee)
        "                         \x1b[38;2;0;0;0m██\x1b[38;2;254;254;254m",
        "                          \x1b[38;2;0;0;0m██\x1b[0m",
    ]
    BLACK_ON_WHITE = "\x1b[38;2;0;0;0m\x1b[48;2;254;254;254m"
    RESET = "\x1b[0m\x1b[38;2;254;254;254m"
    fact_chars = list(fact)
    fact_idx = 0
    filled_lines = []
    for idx, line in enumerate(bubble_lines):
        # Only fill the main bubble, not the tail or empty lines
        if 2 <= idx <= 6:
            new_line = ""
            i = 0
            while i < len(line):
                if line[i:i+19] == "\x1b[38;2;254;254;254m":
                    new_line += line[i:i+19]
                    i += 19
                    if idx == 2:
                        # Fill first inner line with white █
                        while i < len(line) and line[i] == "█":
                            new_line += "█"
                            i += 1
                    else:
                        while i < len(line) and line[i] == "█":
                            if fact_idx < len(fact_chars):
                                new_line += BLACK_ON_WHITE + fact_chars[fact_idx] + RESET
                                fact_idx += 1
                            else:
                                new_line += "█"
                            i += 1
                else:
                    new_line += line[i]
                    i += 1
            filled_lines.append(new_line)
        else:
            filled_lines.append(line)
    manatee_art = '''
                         \x1b[38;2;1;0;0m██\x1b[38;2;0;0;0m 
                        \x1b[38;2;1;0;0m██\x1b[38;2;0;0;0m  
                        \x1b[38;2;0;0;0m█                     
\x1b[38;2;0;0;0m             \x1b[38;2;2;3;5m█\x1b[38;2;4;5;9m█\x1b[38;2;1;2;4m██\x1b[38;2;2;3;5m█\x1b[38;2;0;0;0m    
\x1b[38;2;0;0;0m            \x1b[38;2;8;17;24m█\x1b[38;2;197;214;221m█\x1b[38;2;196;213;221m█\x1b[38;2;195;213;220m██\x1b[38;2;198;212;220m█\x1b[38;2;0;3;7m█\x1b[38;2;0;0;0m   
\x1b[38;2;0;0;0m       \x1b[38;2;0;2;10m█\x1b[38;2;0;2;11m█\x1b[38;2;196;208;214m█\x1b[38;2;234;239;242m█\x1b[38;2;197;209;215m█\x1b[38;2;198;214;223m█\x1b[38;2;198;215;223m█\x1b[38;2;197;214;222m█\x1b[38;2;195;213;220m█\x1b[38;2;194;211;218m█\x1b[38;2;198;213;219m█\x1b[38;2;197;211;219m█\x1b[38;2;197;206;212m█\x1b[38;2;0;0;0m  
\x1b[38;2;0;0;0m     \x1b[38;2;0;5;14m \x1b[38;2;2;2;4m█\x1b[38;2;194;212;218m█\x1b[38;2;243;243;248m█\x1b[38;2;200;213;220m█\x1b[38;2;195;214;224m█\x1b[38;2;198;215;223m█\x1b[38;2;197;214;222m█\x1b[38;2;198;215;223m█\x1b[38;2;195;214;223m█\x1b[38;2;241;243;246m█\x1b[38;2;156;166;168m█\x1b[38;2;195;213;220m█\x1b[38;2;197;211;219m█\x1b[38;2;74;77;82m█\x1b[38;2;0;0;0m  
\x1b[38;2;0;0;0m     \x1b[38;2;81;90;95m█\x1b[38;2;243;242;247m█\x1b[38;2;242;243;245m█\x1b[38;2;198;213;220m█\x1b[38;2;196;214;222m█\x1b[38;2;198;215;222m█\x1b[38;2;198;215;223m█\x1b[38;2;198;215;222m█\x1b[38;2;198;215;223m█\x1b[38;2;197;213;221m█\x1b[38;2;75;76;80m█\x1b[38;2;156;165;170m█\x1b[38;2;195;212;219m█\x1b[38;2;0;2;3m█\x1b[38;2;2;7;10m█\x1b[38;2;1;5;11m█\x1b[38;2;0;0;0m 
\x1b[38;2;0;0;0m    \x1b[38;2;3;2;4m█\x1b[38;2;215;225;227m█\x1b[38;2;197;212;220m█\x1b[38;2;195;215;222m█\x1b[38;2;197;213;221m█\x1b[38;2;197;213;222m██\x1b[38;2;197;213;221m█\x1b[38;2;198;214;222m█\x1b[38;2;200;214;223m█\x1b[38;2;197;213;222m█\x1b[38;2;195;213;220m█\x1b[38;2;198;212;218m█\x1b[38;2;0;2;7m█\x1b[38;2;200;210;219m█\x1b[38;2;197;217;224m█\x1b[38;2;197;215;223m█\x1b[38;2;0;5;6m█
\x1b[38;2;0;0;0m   \x1b[38;2;0;2;8m█\x1b[38;2;200;215;222m█\x1b[38;2;196;211;218m█\x1b[38;2;196;213;220m█\x1b[38;2;195;212;220m█\x1b[38;2;198;215;223m█\x1b[38;2;195;213;220m█\x1b[38;2;196;212;220m█\x1b[38;2;197;214;221m█\x1b[38;2;198;214;223m█\x1b[38;2;199;216;224m█\x1b[38;2;197;214;222m█\x1b[38;2;198;213;220m█\x1b[38;2;73;84;89m█\x1b[38;2;197;211;216m█\x1b[38;2;195;205;214m█\x1b[38;2;7;11;16m█\x1b[38;2;195;213;219m█\x1b[38;2;3;4;8m█
\x1b[38;2;0;0;0m  \x1b[38;2;1;5;9m█\x1b[38;2;201;215;220m█\x1b[38;2;195;213;220m█\x1b[38;2;197;214;221m█\x1b[38;2;198;213;220m█\x1b[38;2;195;213;220m████\x1b[38;2;195;212;220m██\x1b[38;2;198;215;222m█\x1b[38;2;195;214;220m█\x1b[38;2;195;212;219m█\x1b[38;2;196;212;219m█\x1b[38;2;1;2;6m█\x1b[38;2;2;2;4m█\x1b[38;2;163;176;186m█\x1b[38;2;1;6;6m█\x1b[38;2;0;0;0m 
\x1b[38;2;0;0;0m  \x1b[38;2;1;5;9m█\x1b[38;2;198;211;221m█\x1b[38;2;195;213;219m█\x1b[38;2;195;213;220m█\x1b[38;2;198;213;220m█\x1b[38;2;195;213;219m██\x1b[38;2;195;213;220m█\x1b[38;2;197;214;221m█\x1b[38;2;195;213;220m█\x1b[38;2;195;213;219m█\x1b[38;2;197;215;222m█\x1b[38;2;5;3;4m█\x1b[38;2;195;213;220m█\x1b[38;2;171;188;196m█\x1b[38;2;158;173;181m█\x1b[38;2;159;173;181m█\x1b[38;2;5;5;9m█\x1b[38;2;0;0;0m  
\x1b[38;2;0;0;0m  \x1b[38;2;4;5;10m█\x1b[38;2;198;212;217m█\x1b[38;2;195;213;220m█\x1b[38;2;199;214;221m█\x1b[38;2;196;212;219m██\x1b[38;2;195;212;219m█\x1b[38;2;195;212;220m█\x1b[38;2;201;211;218m█\x1b[38;2;198;215;222m█\x1b[38;2;195;210;216m█\x1b[38;2;197;215;225m█\x1b[38;2;160;174;183m█\x1b[38;2;0;4;7m█\x1b[38;2;0;3;5m█\x1b[38;2;0;0;5m█\x1b[38;2;1;2;6m█\x1b[38;2;0;0;0m   
\x1b[38;2;0;0;0m  \x1b[38;2;4;3;7m█\x1b[38;2;198;211;221m█\x1b[38;2;195;212;220m█\x1b[38;2;195;211;218m█\x1b[38;2;196;213;220m█\x1b[38;2;197;213;221m█\x1b[38;2;198;215;222m█\x1b[38;2;1;9;13m█\x1b[38;2;198;212;218m█\x1b[38;2;11;19;22m█\x1b[38;2;163;178;185m█\x1b[38;2;1;10;9m█\x1b[38;2;0;7;10m█\x1b[38;2;159;172;178m█\x1b[38;2;159;174;181m█\x1b[38;2;0;3;4m█\x1b[38;2;0;0;0m   
\x1b[38;2;0;0;0m \x1b[38;2;2;8;10m█\x1b[38;2;196;214;221m█\x1b[38;2;199;215;222m█\x1b[38;2;197;213;221m█\x1b[38;2;196;214;221m█\x1b[38;2;197;213;221m█\x1b[38;2;198;215;222m█\x1b[38;2;197;213;221m█\x1b[38;2;2;8;12m█\x1b[38;2;196;214;221m█\x1b[38;2;195;214;220m█\x1b[38;2;1;5;8m█\x1b[38;2;2;5;7m█\x1b[38;2;0;0;0m \x1b[38;2;2;3;5m█\x1b[38;2;157;174;181m█\x1b[38;2;161;176;181m█\x1b[38;2;7;3;3m█\x1b[38;2;0;0;0m   
\x1b[38;2;3;7;8m█\x1b[38;2;197;214;221m█\x1b[38;2;201;218;225m█\x1b[38;2;196;218;224m█\x1b[38;2;199;218;224m█\x1b[38;2;197;216;222m██\x1b[38;2;199;218;224m█\x1b[38;2;197;217;222m█\x1b[38;2;197;213;218m█\x1b[38;2;198;217;223m█\x1b[38;2;195;218;223m█\x1b[38;2;0;8;16m█\x1b[38;2;0;0;0m  \x1b[38;2;5;5;11m█\x1b[38;2;161;178;185m█\x1b[38;2;2;8;7m█\x1b[38;2;0;0;0m    
\x1b[38;2;3;7;8m█\x1b[38;2;197;214;221m█\x1b[38;2;198;217;222m█\x1b[38;2;3;11;13m█\x1b[38;2;3;13;15m█\x1b[38;2;15;16;14m█\x1b[38;2;2;7;14m█\x1b[38;2;2;7;12m█\x1b[38;2;3;6;14m█\x1b[38;2;198;212;218m█\x1b[38;2;198;217;223m█\x1b[38;2;195;218;223m█\x1b[38;2;0;6;14m█\x1b[38;2;0;0;0m   \x1b[38;2;2;6;12m█\x1b[38;2;0;0;0m     
\x1b[38;2;15;16;18m█\x1b[38;2;198;217;223m█\x1b[38;2;159;178;184m█\x1b[38;2;160;178;185m█\x1b[38;2;162;180;187m█\x1b[38;2;0;9;21m█\x1b[38;2;0;0;0m   \x1b[38;2;0;4;9m█\x1b[38;2;198;217;223m█\x1b[38;2;195;218;223m█\x1b[38;2;1;7;15m█\x1b[38;2;0;0;0m         
\x1b[38;2;3;5;7m█\x1b[38;2;197;217;223m█\x1b[38;2;160;177;184m█\x1b[38;2;161;178;185m██\x1b[38;2;99;110;123m█\x1b[38;2;0;0;0m    \x1b[38;2;4;8;9m█\x1b[38;2;0;8;9m█\x1b[38;2;0;0;0m          
\x1b[38;2;5;7;8m█\x1b[38;2;198;217;223m█\x1b[38;2;165;180;187m█\x1b[38;2;161;179;187m█\x1b[38;2;161;178;186m█\x1b[38;2;99;109;116m█\x1b[38;2;0;0;0m                
\x1b[38;2;6;10;13m█\x1b[38;2;199;220;229m█\x1b[38;2;163;182;189m██\x1b[38;2;160;181;190m█\x1b[38;2;109;110;111m█\x1b[38;2;0;0;0m                
\x1b[38;2;0;0;0m \x1b[38;2;5;13;16m█\x1b[38;2;198;215;222m█\x1b[38;2;160;177;184m█\x1b[38;2;7;8;12m█\x1b[38;2;0;0;0m                 
\x1b[38;2;0;0;0m \x1b[38;2;23;23;23m \x1b[38;2;2;6;5m█\x1b[38;2;3;7;8m█\x1b[38;2;0;0;0m                  \x1b[0m
'''
    if vibe:
        for idx, line in enumerate(filled_lines):
            filled_lines[idx] = rainbowify_ansi(line)
        manatee_art = '\n'.join([rainbowify_ansi(l) for l in manatee_art.split('\n')])
    for l in filled_lines:
        print(l)
    print(manatee_art, end="")

def embed_fact_in_bubble(bubble_art, fact):
    """
    Replace each '█' in bubble_art with a character from fact.
    If fact is too short, fill with spaces. If too long, truncate.
    """
    fact_chars = list(fact)
    fact_len = len(fact_chars)
    fact_idx = 0
    result = ""
    for c in bubble_art:
        if c == "█":
            if fact_idx < fact_len:
                result += fact_chars[fact_idx]
                fact_idx += 1
            else:
                result += " "
        else:
            result += c
    return result

def main():
    import sys
    cursed_mode = "--cursed" in sys.argv
    vibe_mode = "--vibe" in sys.argv
    legacy_mode = "--legacy" in sys.argv
    if legacy_mode:
        obscuratee_legacy(vibe=vibe_mode)
    else:
        obscuratee(vibe=cursed_mode)

if __name__ == "__main__":
    main()
