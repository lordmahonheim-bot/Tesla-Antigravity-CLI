import re

def main():
    assets_path = '/home/lord-mahonheim/bifrost/tesla/OUTPUTS/Synergy/N1/arcanis_base64_assets_hd.md'
    template_path = '/home/lord-mahonheim/bifrost/tesla/Cluedo/template.html'
    output_path = '/home/lord-mahonheim/bifrost/tesla/Cluedo/manuel_cluedo.html'

    print("Reading assets...")
    with open(assets_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # Extract images using regex
    # Format is:
    # ## 1.jpg
    # ```text
    # data:image/jpeg;base64,...
    # ```
    
    pattern = re.compile(r'##\s+(.*?\.jpg)\s+```text\s+(data:image/jpeg;base64,[A-Za-z0-9+/=]+)\s+```', re.DOTALL)
    matches = pattern.findall(content)
    
    images = {}
    for name, base64_data in matches:
        # e.g., '1.jpg' -> 'img_1'
        key = name.replace('.jpg', '')
        images[f'img_{key}'] = base64_data
    
    print(f"Extracted {len(images)} images.")
    
    print("Reading template...")
    with open(template_path, 'r', encoding='utf-8') as f:
        html = f.read()
        
    print("Replacing placeholders...")
    for key, data in images.items():
        placeholder = f"{{{{{key}}}}}"
        html = html.replace(placeholder, data)
        
    print("Writing output...")
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(html)
        
    print("Done! Output saved to", output_path)

if __name__ == '__main__':
    main()
