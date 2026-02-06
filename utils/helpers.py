from config import ADMIN_ID, ADMIN_CHANNEL_ID

async def notify_admins_new_order(bot, order_id, total_amount, user, items, phone, address, location=None):
    # 1. Notify ADMIN_ID (Just Food Items)
    items_text = "\n".join([f"▫️ {i['name']} x {i['quantity']}" for i in items])
    admin_message = (
        f"🆕 <b>Yangi buyurtma #{order_id}</b>\n\n"
        f"🍛 <b>Buyurtma:</b>\n{items_text}"
    )
    
    admins = ADMIN_ID.split(',')
    for admin_id in admins:
        try:
            await bot.send_message(admin_id, admin_message, parse_mode="HTML")
        except Exception:
            pass

    # 2. Notify ADMIN_CHANNEL_ID (Full Details)
    if ADMIN_CHANNEL_ID:
        full_message = (
            f"🆕 <b>Yangi buyurtma #{order_id}</b>\n"
            f"👤 <b>Mijoz:</b> {user.full_name} {f'(@{user.username})' if user.username else ''}\n"
            f"📞 <b>Telefon:</b> {phone}\n"
            f"📍 <b>Manzil:</b> {address}\n\n"
            f"🍛 <b>Buyurtma tarkibi:</b>\n{items_text}\n\n"
            f"💰 <b>Umumiy summa:</b> {total_amount:,} so'm"
        )
        try:
            from aiogram import types
            
            # Prepare media group (album)
            media = types.MediaGroup()
            has_images = False
            
            for index, item in enumerate(items):
                # sqlite3.Row might not have .get(), use access by key if column exists
                # The query guarantees 'image_url' column exists, but value might be None
                image_url = item['image_url'] if 'image_url' in item.keys() else None
                # Actually sqlite3.Row keys() isn't always available directly on row in some versions, 
                # but accessing by name works if it exists. 
                # Safer: dict(item).get('image_url')
                
                if image_url:
                    # Attach caption to the first image
                    if not has_images:
                         media.attach_photo(image_url, caption=full_message, parse_mode="HTML")
                         has_images = True
                    else:
                         media.attach_photo(image_url)
            
            if has_images:
                await bot.send_media_group(ADMIN_CHANNEL_ID, media=media)
            else:
                # If no images, send text as before
                await bot.send_message(ADMIN_CHANNEL_ID, full_message, parse_mode="HTML")

            # Send location if available
            if location and location.get('lat') and location.get('lon'):
                await bot.send_location(ADMIN_CHANNEL_ID, latitude=location['lat'], longitude=location['lon'])
        except Exception as e:
            print(f"Failed to send to channel: {e}")
            # Fallback to text if album fails
            try:
                await bot.send_message(ADMIN_CHANNEL_ID, full_message, parse_mode="HTML")
            except:
                pass

