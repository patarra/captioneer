#!/usr/bin/env python3
import re
from deep_translator import GoogleTranslator

def translate_srt(input_file, output_file):
    """Translate an SRT subtitle file from English to Spanish."""
    translator = GoogleTranslator(source='en', target='es')

    with open(input_file, 'r', encoding='utf-8') as f:
        content = f.read()

    # Split the content into subtitle blocks
    blocks = re.split(r'\n\n+', content.strip())

    translated_blocks = []

    for block in blocks:
        lines = block.split('\n')

        if len(lines) < 3:
            # Skip malformed blocks
            translated_blocks.append(block)
            continue

        # First line is the subtitle number
        subtitle_num = lines[0]

        # Second line is the timestamp
        timestamp = lines[1]

        # Remaining lines are the text to translate
        text_lines = lines[2:]
        text = ' '.join(text_lines)

        # Translate the text
        try:
            translated_text = translator.translate(text)
            print(f"Translating block {subtitle_num}...")
        except Exception as e:
            print(f"Error translating block {subtitle_num}: {e}")
            translated_text = text

        # Reconstruct the block
        translated_block = f"{subtitle_num}\n{timestamp}\n{translated_text}"
        translated_blocks.append(translated_block)

    # Write the translated content to output file
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write('\n\n'.join(translated_blocks))

    print(f"\nTranslation complete! Output saved to: {output_file}")

if __name__ == "__main__":
    input_file = "Dance Tutorial - Il Divo - Hasta mi final_5min.srt"
    output_file = "Dance Tutorial - Il Divo - Hasta mi final_5min_es.srt"

    translate_srt(input_file, output_file)
