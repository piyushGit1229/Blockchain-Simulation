import qrcode

def generate_qr_code(user_id):
    # Generate QR code with user ID
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    qr.add_data(user_id)
    qr.make(fit=True)
    
    img = qr.make_image(fill='black', back_color='white')
    img.save(f'{user_id}_qr.png')  # Save as image

# Generate QR code for a user
user_id = "user1"  # Replace with your user's unique ID
generate_qr_code(user_id)
