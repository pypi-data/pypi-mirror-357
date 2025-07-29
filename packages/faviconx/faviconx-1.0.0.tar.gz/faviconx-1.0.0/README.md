# FaviconX 🎨

A powerful command-line tool for generating favicons from source images. Automatically creates all standard favicon sizes and generates an `index.html` file with proper meta tags.

## Features

- ✅ Generates all standard favicon sizes (16x16 to 1024x1024)
- ✅ Creates ICO, SVG, and PNG formats
- ✅ Apple Touch Icons for iOS devices
- ✅ Android Chrome Icons for PWA support
- ✅ Microsoft Tile support
- ✅ Automatic HTML generation with proper meta tags
- ✅ Web App Manifest for PWA support
- ✅ High-quality image resizing with LANCZOS algorithm
- ✅ Support for various input formats (PNG, JPG, SVG, etc.)

## Installation

1. **Clone or download this repository**
   ```bash
   git clone https://github.com/rapidrabbitsoft/faviconx
   cd faviconx
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Make the script executable (optional)**
   ```bash
   chmod +x faviconx.py
   ```

## Usage

### Basic Usage

```bash
python faviconx.py <source_image> <output_directory>
```

### Examples

```bash
# Generate favicons from a logo
python faviconx.py logo.png ./favicons

# Generate favicons with verbose output
python faviconx.py logo.png ./favicons --verbose

# Generate only favicons (skip HTML files)
python faviconx.py logo.png ./favicons --no-html
```

### Command Line Options

- `source_image`: Path to your source image file
- `output_directory`: Directory where favicons will be saved
- `--no-html`: Skip generating index.html and webmanifest files
- `--verbose, -v`: Enable verbose output

## Generated Files

The tool generates the following files:

### Favicon Files
- `favicon.ico` - Multi-size ICO file (16x16, 32x32, 48x48)
- `favicon.svg` - SVG favicon
- `favicon-16x16.png` to `favicon-1024x1024.png` - PNG favicons in all sizes

### Apple Touch Icons
- `apple-touch-icon-180x180.png`
- `apple-touch-icon-167x167.png`
- `apple-touch-icon-152x152.png`
- `apple-touch-icon-120x120.png`

### Android Chrome Icons
- `android-chrome-192x192.png`
- `android-chrome-512x512.png`

### HTML Files
- `index.html` - Complete HTML file with all favicon meta tags
- `site.webmanifest` - Web App Manifest for PWA support

## Supported Input Formats

- PNG
- JPEG/JPG
- GIF
- BMP
- TIFF
- WebP
- SVG (basic support)

## Favicon Sizes Generated

The tool generates favicons in the following sizes:

- 16×16
- 32×32
- 48×48
- 64×64
- 57×57
- 72×72
- 96×96
- 114×114
- 120×120
- 128×128
- 144×144
- 150×150
- 152×152
- 167×167
- 180×180
- 192×192
- 256×256
- 384×384
- 512×512
- 1024×1024

## Favicon Icon Matrix

| Size      | Filename         | Usage                                                        | Status      |
|-----------|------------------|--------------------------------------------------------------|-------------|
| ICO       | .ico             | Windows icon format. Contains multiple sizes in one file.     | Required    |
| 16×16     | 16×16.png        | Browser tab favicon (classic). Minimum for all browsers.      | Required    |
| SVG       | .svg             | Scalable vector format. Crisp at any size.                   | Required    |
| 32×32     | 32×32.png        | High-DPI favicons / pinned tabs. Retina screens, previews.   | Recommended |
| 48×48     | 48×48.png        | Windows .ico format (legacy). Included in .ico bundles.      | Optional    |
| 64×64     | 64×64.png        | Windows 7+ tile icon (legacy). Rarely used now.              | Optional    |
| 57×57     | 57×57.png        | iOS 6 (iPhone 1–3) home screen. Deprecated, backward compat. | Legacy      |
| 72×72     | 72×72.png        | iOS 6 (iPad). For old iPad models.                           | Legacy      |
| 96×96     | 96×96.png        | Android 2.3+ launcher icons (deprecated). Historical support.| Optional    |
| 114×114   | 114×114.png      | iPhone Retina (iOS 4–6). Useful for legacy iPhones.          | Optional    |
| 120×120   | 120×120.png      | iPhone Retina (iOS 7+). Still used on some devices.          | Recommended |
| 128×128   | 128×128.png      | Chrome Web Store app icon (legacy). Only for Chrome apps.    | Optional    |
| 144×144   | 144×144.png      | Windows 8+ tile icon. Required for Microsoft tiles.          | Recommended |
| 150×150   | 150×150.png      | Microsoft Teams / Outlook preview. Some MS services prefer.  | Optional    |
| 152×152   | 152×152.png      | iPad Retina (iOS 7+). Common for newer iPads.                | Recommended |
| 167×167   | 167×167.png      | iPad Pro Retina. Used in newer iPads (Pro).                  | Recommended |
| 180×180   | 180×180.png      | iOS Safari home screen (iOS 8+). Most used for iOS.          | Required    |
| 192×192   | 192×192.png      | Android Chrome home screen / PWA icon. Must-have for PWAs.   | Required    |
| 256×256   | 256×256.png      | Windows & Linux high-res icons. Some desktop envs.           | Optional    |
| 384×384   | 384×384.png      | Android launcher (high-res devices). High-DPI Android.       | Optional    |
| 512×512   | 512×512.png      | Android splash / PWA install dialog icon. Manifest required. | Required    |
| 1024×1024 | 1024×1024.png    | iOS App Store icons (native apps, not web). For completeness.| Optional    |

**Legend:**
- **Required**: R
- **Recommended**: RC
- **Optional**: O
- **Legacy**: L

## HTML Meta Tags Included

The generated `index.html` includes comprehensive meta tags for:

- Standard favicon support
- Apple Touch Icons
- Android Chrome Icons
- Microsoft Tiles
- Web App Manifest
- PWA support
- Mobile web app capabilities

## Requirements

- Python 3.9+
- Pillow (PIL)
- Click
- CairoSVG

## Troubleshooting

### Common Issues

1. **"Source image not found"**
   - Make sure the path to your source image is correct
   - Use absolute paths if needed

2. **Permission errors**
   - Ensure you have write permissions for the output directory
   - Create the output directory manually if needed

3. **Image format not supported**
   - Convert your image to PNG or JPEG format
   - Ensure the image file is not corrupted

### Tips for Best Results

1. **Use high-resolution source images** (at least 512x512 pixels)
2. **Use PNG format** for source images with transparency
3. **Ensure your logo has good contrast** for small sizes
4. **Test the generated favicons** in different browsers and devices

## Browser Support

The generated favicons support:

- Chrome/Chromium
- Firefox
- Safari
- Edge
- Internet Explorer 11+
- Mobile browsers (iOS Safari, Chrome Mobile)

## License

This project is open source and available under the MIT License.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## Support

If you encounter any issues or have questions, please open an issue on the [repository](https://github.com/rapidrabbitsoft/faviconx). 