#!/usr/bin/env python3
"""
FaviconX - A command line tool for generating favicons from source images.
Generates all standard favicon sizes and creates an index.html with proper meta tags.
"""

import os
import sys
from pathlib import Path
from typing import List, Tuple
import click
from PIL import Image, ImageOps
import cairosvg
import io
import textwrap


class FaviconGenerator:
    """Generates favicons in various sizes from a source image, based on option filter and filename prefix."""
    
    # Standard favicon sizes
    FAVICON_SIZES = [
        (16, 16),
        (32, 32),
        (48, 48),
        (64, 64),
        (57, 57),
        (72, 72),
        (96, 96),
        (114, 114),
        (120, 120),
        (128, 128),
        (144, 144),
        (150, 150),
        (152, 152),
        (167, 167),
        (180, 180),
        (192, 192),
        (256, 256),
        (384, 384),
        (512, 512),
        (1024, 1024),
    ]
    
    def __init__(self, source_path: str, output_path: str, icon_options=None, prefix="icon"):
        """Initialize the favicon generator.
        
        Args:
            source_path: Path to the source image
            output_path: Directory to save generated favicons
            icon_options: Set of icon options to generate
            prefix: Prefix for all generated favicon files
        """
        self.source_path = Path(source_path)
        self.output_path = Path(output_path)
        self.output_path.mkdir(parents=True, exist_ok=True)
        if icon_options is None:
            icon_options = {"Required", "Recommended", "Optional", "Legacy"}
        self.icon_options = set(icon_options)
        self.generated_icons = []  # List of dicts from ICON_SIZES that were generated
        self.prefix = prefix
        
    def should_generate(self, icon):
        if "all" in self.icon_options:
            return True
        return icon["option"] in self.icon_options
    
    def get_filename(self, icon):
        # Replace 'favicon' with prefix in filename
        if icon["filename"].startswith("favicon"):
            return icon["filename"].replace("favicon", self.prefix, 1)
        return icon["filename"]
    
    def load_source_image(self) -> Image.Image:
        """Load and prepare the source image.
        
        Returns:
            PIL Image object
        """
        if not self.source_path.exists():
            raise FileNotFoundError(f"Source image not found: {self.source_path}")
        
        # Handle SVG files by converting to PNG first
        if self.source_path.suffix.lower() == '.svg':
            try:
                import cairosvg
                import io
                
                # Convert SVG to PNG bytes
                png_data = cairosvg.svg2png(url=str(self.source_path))
                
                # Create PIL Image from PNG bytes
                image = Image.open(io.BytesIO(png_data))
                
                # Convert to RGBA if not already
                if image.mode != 'RGBA':
                    image = image.convert('RGBA')
                    
                return image
                
            except ImportError:
                raise ImportError("CairoSVG is required to process SVG files. Install with: pip install cairosvg")
            except Exception as e:
                raise Exception(f"Error converting SVG to PNG: {e}")
        else:
            # Load regular image formats
            image = Image.open(self.source_path)
            
            # Convert to RGBA if not already
            if image.mode != 'RGBA':
                image = image.convert('RGBA')
                
            return image
    
    def resize_image(self, image: Image.Image, size: Tuple[int, int]) -> Image.Image:
        """Resize image to specified size with high quality.
        
        Args:
            image: Source image
            size: Target size (width, height)
            
        Returns:
            Resized image
        """
        # Use LANCZOS for high quality resizing
        resized = image.resize(size, Image.Resampling.LANCZOS)
        return resized
    
    def generate_png_favicon(self, image: Image.Image, size: Tuple[int, int], filename: str):
        """Generate a PNG favicon of specified size.
        
        Args:
            image: Source image
            size: Target size
            filename: Output filename
        """
        resized = self.resize_image(image, size)
        output_file = self.output_path / filename
        resized.save(output_file, 'PNG', optimize=True)
        return output_file
    
    def generate_ico_favicon(self, image: Image.Image, filename: str):
        """Generate ICO favicon with multiple sizes.
        
        Args:
            image: Source image
            filename: Output filename
        """
        # ICO files typically contain multiple sizes
        ico_sizes = [(16, 16), (32, 32), (48, 48)]
        images = [self.resize_image(image, size) for size in ico_sizes]
        
        output_file = self.output_path / filename
        images[0].save(
            output_file,
            format='ICO',
            sizes=[(img.width, img.height) for img in images],
            append_images=images[1:]
        )
        return output_file
    
    def generate_svg_favicon(self, image: Image.Image, filename: str):
        """Generate SVG favicon from the source image.
        
        Args:
            image: Source image
            filename: Output filename
        """
        # For SVG, we'll create a simple SVG that references the original image
        # This is a basic approach - for more complex SVGs, you might want to vectorize the image
        
        # Convert image to base64 for embedding
        import base64
        buffer = io.BytesIO()
        image.save(buffer, format='PNG')
        img_data = base64.b64encode(buffer.getvalue()).decode()
        
        svg_content = f'''<?xml version="1.0" encoding="UTF-8"?>\n<svg width="32" height="32" viewBox="0 0 32 32" xmlns="http://www.w3.org/2000/svg">\n  <image href="data:image/png;base64,{img_data}" width="32" height="32"/>\n</svg>'''
        
        output_file = self.output_path / filename
        with open(output_file, 'w') as f:
            f.write(svg_content)
        return output_file
    
    def generate_all_favicons(self):
        """Generate all favicon sizes and formats."""
        try:
            image = self.load_source_image()
            click.secho(f"Loaded source image: {self.source_path}", fg="cyan", bold=True)
            for icon in ICON_SIZES:
                if not self.should_generate(icon):
                    continue
                filename = self.get_filename(icon)
                generated = False
                if icon["size"] == "ICO":
                    self.generate_ico_favicon(image, filename)
                    generated = True
                elif icon["size"] == "SVG":
                    self.generate_svg_favicon(image, filename)
                    generated = True
                else:
                    try:
                        w, h = [int(x) for x in icon["size"].replace('×', 'x').split('x')]
                        self.generate_png_favicon(image, (w, h), filename)
                        generated = True
                    except Exception:
                        pass
                icon_copy = icon.copy()
                icon_copy["generated"] = generated
                icon_copy["actual_filename"] = filename
                self.generated_icons.append(icon_copy)
            click.secho("\nFavicons generated!", fg="green", bold=True)
        except Exception as e:
            click.secho(f"Error generating favicons: {e}", fg="red", bold=True, err=True)
            sys.exit(1)

    def print_summary_table(self):
        header = f"{'Size':<10} {'Filename':<24} {'Option':<12} {'Generated':<10} Usage"
        click.secho("\nFavicon Generation Summary:", fg="magenta", bold=True)
        click.secho(header, bold=True)
        click.secho("-" * len(header), fg="magenta")
        for icon in ICON_SIZES:
            actual_filename = self.get_filename(icon)
            generated = next((i["generated"] for i in self.generated_icons if i["actual_filename"] == actual_filename), False)
            color = "green" if generated else "yellow"
            option_color = {
                "Required": "green",
                "Recommended": "cyan",
                "Optional": "yellow",
                "Legacy": "white"
            }.get(icon['option'], "white")
            click.secho(f"{icon['size']:<10} {actual_filename:<24} ", nl=False)
            click.secho(f"{icon['option']:<12}", fg=option_color, nl=False)
            click.secho(f"{('Yes' if generated else 'No'):<10}", fg=color, nl=False)
            click.secho(f"{icon['usage']}")


class HTMLGenerator:
    """Generates index.html and webmanifest with meta tags for generated icons only."""
    
    def __init__(self, output_path: str, generated_icons):
        """Initialize HTML generator.
        
        Args:
            output_path: Directory where favicons are saved
            generated_icons: List of generated icons
        """
        self.output_path = Path(output_path)
        self.generated_icons = generated_icons
    
    def generate_html(self):
        """Generate index.html with all favicon meta tags."""
        # Only include meta tags for generated icons
        meta_tags = []
        for icon in self.generated_icons:
            if not icon.get("generated"):
                continue
            size = icon["size"]
            filename = icon["actual_filename"]
            if size == "ICO":
                meta_tags.append(f'<link rel="icon" type="image/x-icon" href="{filename}">')
            elif size == "SVG":
                meta_tags.append(f'<link rel="icon" type="image/svg+xml" href="{filename}">')
            elif "apple" in filename or size in ["180×180", "167×167", "152×152", "120×120", "57×57", "72×72", "114×114", "144×144", "150×150"]:
                meta_tags.append(f'<link rel="apple-touch-icon" sizes="{size}" href="{filename}">')
            elif size in ["192×192", "512×512"]:
                meta_tags.append(f'<link rel="icon" type="image/png" sizes="{size}" href="{filename}">')
            elif filename.endswith(".png"):
                # General PNG favicon
                meta_tags.append(f'<link rel="icon" type="image/png" sizes="{size}" href="{filename}">')
        
        meta_tags_str = '\n    '.join(meta_tags)
        html_content = f'''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Your Website</title>
    {meta_tags_str}
    <meta name="theme-color" content="#ffffff">
</head>
<body>
    <h1>Welcome to Your Website</h1>
    <p>Your favicons have been generated successfully!</p>
    <p>Check the browser tab to see your favicon in action.</p>
</body>
</html>'''
        
        output_file = self.output_path / 'index.html'
        with open(output_file, 'w') as f:
            f.write(html_content)
        
        click.echo(f"Generated: {output_file}")
    
    def generate_webmanifest(self):
        """Generate site.webmanifest file for PWA support."""
        # Only include icons that are generated and are 192x192 or 512x512
        manifest_icons = []
        for icon in self.generated_icons:
            if not icon.get("generated"):
                continue
            if icon["size"] in ["192×192", "512×512"]:
                manifest_icons.append({
                    "src": icon["actual_filename"],
                    "sizes": icon["size"],
                    "type": "image/png"
                })
        manifest_content = {
            "name": "Your Website",
            "short_name": "Your App",
            "description": "Your website description",
            "start_url": "/",
            "display": "standalone",
            "background_color": "#ffffff",
            "theme_color": "#ffffff",
            "icons": manifest_icons
        }
        import json
        output_file = self.output_path / 'site.webmanifest'
        with open(output_file, 'w') as f:
            json.dump(manifest_content, f, indent=2)
        
        click.echo(f"Generated: {output_file}")


# Icon matrix for favicon generation and documentation
ICON_SIZES = [
    {"size": "ICO", "filename": "favicon.ico", "usage": "Windows icon format. Contains multiple sizes in one file.", "option": "Required"},
    {"size": "16×16", "filename": "favicon-16x16.png", "usage": "Browser tab favicon (classic). Minimum requirement for all browsers.", "option": "Required"},
    {"size": "SVG", "filename": "favicon.svg", "usage": "Scalable vector format. Perfect for crisp display at any size.", "option": "Required"},
    {"size": "32×32", "filename": "favicon-32x32.png", "usage": "High-DPI favicons / pinned tabs. Used on retina screens, tab previews.", "option": "Recommended"},
    {"size": "48×48", "filename": "favicon-48x48.png", "usage": "Windows .ico format (legacy). Included in .ico bundles.", "option": "Optional"},
    {"size": "64×64", "filename": "favicon-64x64.png", "usage": "Windows 7+ tile icon (legacy). Rarely used now.", "option": "Optional"},
    {"size": "57×57", "filename": "favicon-57x57.png", "usage": "iOS 6 (iPhone 1–3) home screen. Deprecated but used for backward compatibility.", "option": "Legacy"},
    {"size": "72×72", "filename": "favicon-72x72.png", "usage": "iOS 6 (iPad). For old iPad models.", "option": "Legacy"},
    {"size": "96×96", "filename": "favicon-96x96.png", "usage": "Android 2.3+ launcher icons (deprecated). Historical support.", "option": "Optional"},
    {"size": "114×114", "filename": "favicon-114x114.png", "usage": "iPhone Retina (iOS 4–6). Useful for legacy iPhones.", "option": "Optional"},
    {"size": "120×120", "filename": "favicon-120x120.png", "usage": "iPhone Retina (iOS 7+). Still used on some devices.", "option": "Recommended"},
    {"size": "128×128", "filename": "favicon-128x128.png", "usage": "Chrome Web Store app icon (legacy). Only needed for Chrome Web Store apps.", "option": "Optional"},
    {"size": "144×144", "filename": "favicon-144x144.png", "usage": "Windows 8+ tile icon. Required for Microsoft tiles.", "option": "Recommended"},
    {"size": "150×150", "filename": "favicon-150x150.png", "usage": "Microsoft Teams / Outlook preview. Some Microsoft services prefer this.", "option": "Optional"},
    {"size": "152×152", "filename": "favicon-152x152.png", "usage": "iPad Retina (iOS 7+). Common for newer iPads.", "option": "Recommended"},
    {"size": "167×167", "filename": "favicon-167x167.png", "usage": "iPad Pro Retina. Used in newer iPads (Pro).", "option": "Recommended"},
    {"size": "180×180", "filename": "favicon-180x180.png", "usage": "iOS Safari home screen (iOS 8+). Most used for iPhones and iPads added to home screen.", "option": "Required"},
    {"size": "192×192", "filename": "favicon-192x192.png", "usage": "Android Chrome home screen / PWA icon. Must-have for PWAs on Android.", "option": "Required"},
    {"size": "256×256", "filename": "favicon-256x256.png", "usage": "Windows & Linux high-res icons. Used by some desktop environments.", "option": "Optional"},
    {"size": "384×384", "filename": "favicon-384x384.png", "usage": "Android launcher (high-res devices). For high-DPI Android devices.", "option": "Optional"},
    {"size": "512×512", "filename": "favicon-512x512.png", "usage": "Android splash / PWA install dialog icon. Required by manifest.webmanifest.", "option": "Required"},
    {"size": "1024×1024", "filename": "favicon-1024x1024.png", "usage": "iOS App Store icons (for native apps, not web). Not used in web, but can be included for completeness.", "option": "Optional"},
]


@click.command()
@click.argument('source_image', type=click.Path(exists=True, path_type=str))
@click.argument('output_directory', type=click.Path(path_type=str))
@click.option('--no-html', is_flag=True, help='Skip generating index.html and webmanifest files')
@click.option('--verbose', '-v', is_flag=True, help='Enable verbose output')
@click.option('--icon-status', default='R,RC,O,L', show_default=True, help='Comma-separated list of icon statuses to generate: R,RC,O,L,ALL (default: R,RC,O,L)')
@click.option('--prefix', default='icon', show_default=True, help='Prefix for all generated favicon files (default: icon)')
@click.option('--option', type=click.Choice(['required', 'recommended', 'required-recommended', 'optional', 'all']), default='all', show_default=True, help='Filter icons by importance level (default: all)')
def main(source_image: str, output_directory: str, no_html: bool, verbose: bool, icon_status: str, prefix: str, option: str):
    """
    Generate favicons from a source image.
    
    SOURCE_IMAGE: Path to the source image file (PNG, JPG, SVG, etc.)
    OUTPUT_DIRECTORY: Directory where favicons will be saved

    --icon-status: Comma-separated list of icon statuses to generate: R,RC,O,L,ALL (default: R,RC,O,L)
    --prefix: Prefix for all generated favicon files (default: icon)
    --option: Filter icons by importance level: required, recommended, required-recommended, optional, all (default: all)
    """
    # Map option choices to option names
    option_map = {
        'required': {'Required'},
        'recommended': {'Required', 'Recommended'},
        'required-recommended': {'Required', 'Recommended'},
        'optional': {'Required', 'Recommended', 'Optional'},
        'all': {'Required', 'Recommended', 'Optional', 'Legacy'}
    }
    
    # Use option if specified, otherwise use icon_status
    if option != 'all':
        options = option_map[option]
    else:
        # Convert old status codes to new option names
        status_to_option = {
            'R': 'Required',
            'RC': 'Recommended', 
            'O': 'Optional',
            'L': 'Legacy'
        }
        options = {status_to_option.get(s.strip().upper(), 'Required') for s in icon_status.split(",")}
    
    if verbose:
        click.secho(f"Source image: {source_image}", fg="cyan")
        click.secho(f"Output directory: {output_directory}", fg="cyan")
        click.secho(f"Icon options: {options}", fg="cyan")
        click.secho(f"Filename prefix: {prefix}", fg="cyan")
        click.secho(f"Option: {option}", fg="cyan")
    try:
        generator = FaviconGenerator(source_image, output_directory, icon_options=options, prefix=prefix)
        generator.generate_all_favicons()
        if not no_html:
            html_generator = HTMLGenerator(output_directory, generator.generated_icons)
            html_generator.generate_html()
            html_generator.generate_webmanifest()
        generator.print_summary_table()
        click.secho(f"\nFavicon generation complete!", fg="green", bold=True)
        click.secho(f"Output directory: {output_directory}", fg="cyan")
        if not no_html:
            click.secho(f"Open {output_directory}/index.html in your browser to test", fg="magenta")
    except Exception as e:
        click.secho(f"Error: {e}", fg="red", bold=True, err=True)
        sys.exit(1)


if __name__ == '__main__':
    main() 