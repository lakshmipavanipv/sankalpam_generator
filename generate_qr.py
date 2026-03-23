"""
generate_qr.py
──────────────
Generates a QR code that points to your Sankalpam Generator web app.
Run this script once after deploying your frontend to get a QR code
you can print and place at temples or event venues.

Usage:
  python generate_qr.py --url https://your-app.vercel.app
  python generate_qr.py --url http://localhost:3000   # for local testing
"""

import argparse
import os

def generate_qr(url: str, output_file: str = "sankalpam_qr.png"):
    try:
        import qrcode
        from qrcode.image.styledpil import StyledPilImage
        from qrcode.image.styles.moduledrawers import RoundedModuleDrawer

        qr = qrcode.QRCode(
            version=2,
            error_correction=qrcode.constants.ERROR_CORRECT_H,
            box_size=12,
            border=4,
        )
        qr.add_data(url)
        qr.make(fit=True)

        # Generate styled QR with rounded corners
        img = qr.make_image(
            image_factory=StyledPilImage,
            module_drawer=RoundedModuleDrawer()
        )
        img.save(output_file)
        print(f"✅ QR Code saved as: {output_file}")
        print(f"   URL encoded: {url}")
        print(f"   Print and place at your pooja venue!")

    except ImportError:
        # Fallback: basic QR without styling
        try:
            import qrcode
            qr = qrcode.make(url)
            qr.save(output_file)
            print(f"✅ QR Code saved as: {output_file} (basic style)")
            print(f"   To get styled QR: pip install qrcode[pil]")
        except ImportError:
            print("❌ qrcode library not found.")
            print("   Install it: pip install qrcode[pil]")
            return

    # Also print ASCII QR to terminal
    try:
        import qrcode
        qr2 = qrcode.QRCode(border=1)
        qr2.add_data(url)
        qr2.make(fit=True)
        print("\n📱 Terminal QR Preview:")
        qr2.print_ascii()
    except Exception:
        pass


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generate QR code for Sankalpam app")
    parser.add_argument(
        "--url",
        default="http://localhost:3000",
        help="URL of your deployed Sankalpam frontend"
    )
    parser.add_argument(
        "--output",
        default="sankalpam_qr.png",
        help="Output filename for QR code image"
    )
    args = parser.parse_args()
    generate_qr(args.url, args.output)
