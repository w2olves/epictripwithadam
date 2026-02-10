import csv
import os
import re
import shutil
from icrawler.builtin import GoogleImageCrawler, BingImageCrawler

# Mapping of state names to codes (based on the CSV content)
STATE_MAPPING = {
    'California': 'CA',
    'Nevada': 'NV',
    'Arizona': 'AZ',
    'Utah': 'UT',
    'Colorado': 'CO',
    'Montana': 'MT',
    'South Dakota': 'SD',
    'North Dakota': 'ND',
    'Minnesota': 'MN'
}

CSV_FILE = 'poi_by_state.csv'
BASE_OUTPUT_DIR = 'assets/poi'

def image_sort_key(filename):
    name, _ = os.path.splitext(filename)
    if name.isdigit():
        return int(name)
    return 10**9

def normalize_output_dir_images(output_dir):
    # Keep at most 6 jpg files and normalize names to 1.jpg..6.jpg
    files = [f for f in os.listdir(output_dir) if f.lower().endswith('.jpg')]
    files = sorted(files, key=lambda f: (image_sort_key(f), f))

    for filename in files[6:]:
        os.remove(os.path.join(output_dir, filename))

    keep = files[:6]
    temp_names = []
    for idx, filename in enumerate(keep, start=1):
        src = os.path.join(output_dir, filename)
        tmp_name = f"__tmp_norm_{idx}.jpg"
        os.rename(src, os.path.join(output_dir, tmp_name))
        temp_names.append(tmp_name)

    for idx, tmp_name in enumerate(temp_names, start=1):
        os.rename(
            os.path.join(output_dir, tmp_name),
            os.path.join(output_dir, f"{idx}.jpg")
        )

    return len(temp_names)

def normalize_name(name):
    # Determine directory name compatible string
    # Remove special chars, replace spaces with underscores, lowercase
    clean_name = re.sub(r'[^\w\s-]', '', name).strip().lower()
    return re.sub(r'[-\s]+', '_', clean_name)

def get_state_code(state_name):
    return STATE_MAPPING.get(state_name.strip(), 'UNK')

def process_csv():
    if not os.path.exists(CSV_FILE):
        print(f"Error: {CSV_FILE} not found.")
        return

    with open(CSV_FILE, 'r', encoding='utf-8') as f:
        reader = csv.reader(f, delimiter='|')
        # Skip header if it exists (it does: state || interest)
        header = next(reader, None)
        
        # Check if delimiter was actually pipe, if not, try to sniff it or just handle parse
        # The user said "state || interest", so let's check the first line
        if header and '||' in header[0]:
             # It might have been read as one column if delimiter was wrong
             pass

    # Re-reading with custom logic to handle "||" explicitly if csv module fails
    with open(CSV_FILE, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    row_count = 0
    for line in lines:
        if '||' not in line:
            continue
        
        if row_count == 0 and 'state' in line.lower() and 'interest' in line.lower():
             # Header
             row_count += 1
             continue

        parts = line.split('||')
        if len(parts) < 2:
            continue
        
        state_name = parts[0].strip()
        interest_name = parts[1].strip()
        
        state_code = get_state_code(state_name)
        
        # We need a counter for the attraction ID? The user example: UT_01_zion_national_park
        # It seems like there is an index "01". 
        # I need to track the count per state to generate this ID.
        # Let's group by state first or just maintain a counter dict.
        pass

def main():
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('--limit', type=int, help='Limit the number of attractions to process')
    parser.add_argument('--engine', type=str, default='bing', choices=['google', 'bing'], help='Search engine to use (default: bing)')
    args = parser.parse_args()

    # 1. Parse CSV and build a list of tasks
    tasks = []
    state_counters = {code: 0 for code in STATE_MAPPING.values()}
    state_counters['UNK'] = 0

    with open(CSV_FILE, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    print(f"Found {len(lines)} lines in {CSV_FILE}")

    for i, line in enumerate(lines):
        if '||' not in line:
            continue
        
        # Skip header
        if i == 0 and 'state' in line.lower() and 'interest' in line.lower():
            continue

        parts = line.split('||')
        if len(parts) < 2:
            continue
        
        state_name = parts[0].strip()
        interest_name = parts[1].strip()
        state_code = get_state_code(state_name)

        if state_code == 'UNK':
            print(f"Warning: Unknown state '{state_name}' in line: {line.strip()}")
        
        state_counters[state_code] += 1
        count = state_counters[state_code]
        
        # Format: UT_01_zion_national_park
        attraction_slug = normalize_name(interest_name)
        attraction_id = f"{state_code}_{count:02d}_{attraction_slug}"
        
        output_dir = os.path.join(BASE_OUTPUT_DIR, state_code, attraction_id)
        
        tasks.append({
            'interest': interest_name,
            'output_dir': output_dir
        })
        
        if args.limit and len(tasks) >= args.limit:
            break

    print(f"Parsed {len(tasks)} attractions.")

    # 2. execute downloads
    from PIL import Image

    for task in tasks:
        interest = task['interest']
        output_dir = task['output_dir']
        
        # Check if we already have 6 GOOD images
        if os.path.exists(output_dir):
            existing = [f for f in os.listdir(output_dir) if f.lower().endswith('.jpg')]
            if len(existing) >= 6:
                normalize_output_dir_images(output_dir)
                print(f"Skipping {interest}, already has 6 images.")
                continue
        else:
            os.makedirs(output_dir, exist_ok=True)

        print(f"Downloading images for: {interest} -> {output_dir} using {args.engine}")
        
        # Refined query:
        # - Prefer: travel blog, photography, high resolution, 2019..2025
        # - Exclude: watermarks, stock sites
        search_query = (
            f"{interest} +\"travel blog\" +\"photography\" +\"high resolution\" "
            f"-stock -alamy -shutterstock -gettyimages -depositphotos -dreamstime -123rf -istock -vector -clipart"
        )
        
        # Configure crawler
        if args.engine == 'google':
             # Google might support 'size' arg better in valid range, or just use 'large'
             filters = dict(size='large')
             crawler = GoogleImageCrawler(storage={'root_dir': output_dir}, downloader_threads=4)
        else:
             filters = dict(size='large')
             crawler = BingImageCrawler(storage={'root_dir': output_dir}, downloader_threads=4)
        
        # Crawl MORE than needed (e.g. 40) so we can filter out small ones
        crawler.crawl(keyword=search_query, filters=filters, max_num=40, file_idx_offset=0, overwrite=True)
        
        # Post-processing: Filter by resolution and rename
        # Refresh file list
        files = sorted([f for f in os.listdir(output_dir) if f.endswith(('.jpg', '.jpeg', '.png'))])
        
        valid_images = []
        for filename in files:
            filepath = os.path.join(output_dir, filename)
            try:
                with Image.open(filepath) as img:
                    width, height = img.size
                    if width >= 1920:
                        valid_images.append(filename)
            except Exception as e:
                print(f"Error reading {filename}: {e}")
        
        # We want to keep up to 6 valid images.
        images_to_keep = valid_images[:6]
        
        if not images_to_keep:
            print(f"Warning: No valid high-res images found for {interest}")
            # Optional: Clean up everything? Or keep best?
            # User said "no image less than 1920". So keep nothing if none match.
        
        # Create a temp directory to move good files to
        temp_dir = os.path.join(output_dir, "temp_kept")
        if os.path.exists(temp_dir):
            try:
                shutil.rmtree(temp_dir)
            except Exception as e:
                print(f"Error removing temp dir: {e}")
        
        try:
            os.makedirs(temp_dir, exist_ok=True)
        except Exception as e:
             print(f"Error creating temp dir: {e}")
             continue
        
        print(f"Keeping {len(images_to_keep)} images for {interest}...")
        
        import time
        time.sleep(1) # Wait for handles to release
        
        for idx, filename in enumerate(images_to_keep):
            src = os.path.join(output_dir, filename)
            dst = os.path.join(temp_dir, f"{idx+1}.jpg")
            try:
                shutil.copy2(src, dst)
            except Exception as e:
                print(f"Error copying {filename} to temp: {e}")
            
        # Now clear the output directory of ALL files
        for filename in os.listdir(output_dir):
             filepath = os.path.join(output_dir, filename)
             if filename == "temp_kept":
                 continue
             
             try:
                 if os.path.isfile(filepath):
                    os.remove(filepath)
                 elif os.path.isdir(filepath):
                    shutil.rmtree(filepath)
             except Exception as e:
                 print(f"Error deleting {filename}: {e}")
                 
        # Move files back from temp
        for filename in os.listdir(temp_dir):
            src = os.path.join(temp_dir, filename)
            dst = os.path.join(output_dir, filename)
            try:
                shutil.move(src, dst)
            except Exception as e:
                print(f"Error moving {filename} back: {e}")
            
        try:
            os.rmdir(temp_dir)
        except Exception as e:
            print(f"Error removing temp dir: {e}")

        normalize_output_dir_images(output_dir)


if __name__ == "__main__":
    main()
