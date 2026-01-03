
from PIL import Image, ImageDraw, ImageFont
from pillow_heif import register_heif_opener
import os
from pathlib import Path

# تلاش برای وارد کردن rembg؛ در صورت نبود، حذف پس‌زمینه غیرفعال می‌شود
try:
    from rembg import remove as rembg_remove  # برای حذف پس‌زمینه
    REMBG_AVAILABLE = True
except Exception:
    rembg_remove = None
    REMBG_AVAILABLE = False

register_heif_opener()

def edit_woocommerce_images(input_folder, output_folder, size=(800, 800), quality=85, watermark_text=None):
    # مسیرهای ورودی و خروجی را به اشیاء Path تبدیل می‌کنیم
    input_path = Path(input_folder)
    output_path_base = Path(output_folder)

    if not input_path.is_dir():
        print(f"❌ خطا: پوشه ورودی یافت نشد! مسیر را بررسی کنید: {input_path}")
        return

    print(f"✅ پردازش از پوشه: {input_path}")
    print(f"✅ ذخیره‌سازی در پوشه: {output_path_base.resolve()}") # نمایش مسیر کامل

    font_path = "arial.ttf"
    font_size = 50
    try:
        font = ImageFont.truetype(font_path, font_size)
    except IOError:
        print(f"⚠️ هشدار: فونت '{font_path}' یافت نشد. از فونت پیش‌فرض استفاده می‌شود.")
        font = ImageFont.load_default()

    for img_path in input_path.rglob('*'):
               if img_path.is_file() and img_path.suffix.lower() in ['.png', '.jpg', '.jpeg', '.heic', '.webp']:
                try:
                    relative_path = img_path.relative_to(input_path)
                    output_dir = output_path_base / relative_path.parent
                    output_dir.mkdir(parents=True, exist_ok=True)

                    base_filename = img_path.stem
                    output_filename = f"{base_filename}.jpg"
                    final_output_path = output_dir / output_filename
                    
                    print(f"  ⏳ پردازش: {img_path}")

                    img = Image.open(img_path).convert('RGB')
                    if REMBG_AVAILABLE:
                        print(f"    🔄 حذف پس‌زمینه...")
                        img_no_bg = rembg_remove(img).convert('RGBA')
                    else:
                        if img_path.suffix.lower() in ['.png', '.webp']:
                            img_no_bg = Image.open(img_path).convert('RGBA')
                        else:
                            img_no_bg = img.convert('RGBA')
                    
                    print(f"    🔄 تغییر اندازه و وسط چین کردن...")
        
                    img_no_bg.thumbnail(size, Image.Resampling.LANCZOS)
                    width, height = img_no_bg.size

                    new_img = Image.new('RGBA', size, (255, 255, 255, 255))

                    offset = ((size[0] - width) // 2, (size[1] - height) // 2)

                    new_img.paste(img_no_bg, offset, img_no_bg)

                    if watermark_text:
                        draw = ImageDraw.Draw(new_img)
                        text_bbox = draw.textbbox((0, 0), watermark_text, font=font)
                        text_width = text_bbox[2] - text_bbox[0]
                        text_height = text_bbox[3] - text_bbox[1]
                        position = (size[0] - text_width - 10, size[1] - text_height - 10)
                        draw.text(position, watermark_text, fill=(200, 200, 200), font=font)
                    

                    if new_img.mode == 'RGBA':
                        rgb_img = Image.new('RGB', new_img.size, (255, 255, 255))
                        rgb_img.paste(new_img, mask=new_img.split()[-1])  # استفاده از آلفا کانال
                        rgb_img.save(final_output_path, 'JPEG', quality=quality, optimize=True)
                    else:
                        new_img.save(final_output_path, 'JPEG', quality=quality, optimize=True)
                    
                    print(f"  ✔️ ذخیره شد: {final_output_path}")

                except Exception as e:
                    print(f"  ❌ خطا در پردازش فایل {img_path.name}: {e}")

    print("\n✅ عملیات پردازش تمام تصاویر به پایان رسید.")


if __name__ == "__main__":

    input_folder = "f:\Project\image-automation-pipeline\input\عکس تسمه B"
    output_folder = "f:\Project\image-automation-pipeline\output\output_images_edited"
    watermark_text = None
    
    edit_woocommerce_images(
        input_folder=input_folder, 
        output_folder=output_folder, 
        size=(800, 800), 
        quality=85, 
        watermark_text=watermark_text
    )
