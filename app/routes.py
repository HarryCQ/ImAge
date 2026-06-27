import os
import uuid
import io
from werkzeug.utils import secure_filename
from flask import Blueprint, render_template, redirect, url_for, flash, request, current_app, jsonify
from flask_login import login_required, current_user
from app import db
from app.models import User, Image, Exhibition, ExhibitionItem
from app.oss_config import OSS_ENABLED, get_oss_bucket, get_oss_base_url

main_bp = Blueprint('main', __name__)

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp', 'bmp'}

# Total storage limit: 10 GB (in bytes)
TOTAL_STORAGE_LIMIT = 10 * 1024 * 1024 * 1024


def get_total_storage_used():
    """Get the total storage used by all images in bytes."""
    result = db.session.query(db.func.coalesce(db.func.sum(Image.file_size), 0)).scalar()
    return result


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def get_image_url(filename):
    """Get the full URL for an image file (OSS or local)."""
    if OSS_ENABLED:
        return f"{get_oss_base_url()}/{filename}"
    return url_for('static', filename=f'uploads/{filename}')


def save_upload(file):
    """Save uploaded file to OSS or local storage. Returns (filename, file_size)."""
    ext = file.filename.rsplit('.', 1)[1].lower()
    unique_name = f"{uuid.uuid4().hex}.{ext}"

    if OSS_ENABLED:
        # Upload to Alibaba Cloud OSS
        bucket = get_oss_bucket()
        file_data = file.read()
        bucket.put_object(unique_name, file_data)
        file_size = len(file_data)
    else:
        # Save locally
        file.seek(0, os.SEEK_END)
        file_size = file.tell()
        file.seek(0)
        filepath = os.path.join(current_app.config['UPLOAD_FOLDER'], unique_name)
        file.save(filepath)

    return unique_name, file_size


def delete_file(filename):
    """Delete a file from OSS or local storage."""
    if not filename or filename == 'default_avatar.svg':
        return

    if OSS_ENABLED:
        bucket = get_oss_bucket()
        try:
            bucket.delete_object(filename)
        except Exception:
            pass  # File may not exist
    else:
        filepath = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
        if os.path.exists(filepath):
            os.remove(filepath)


@main_bp.route('/')
def index():
    exhibitions = Exhibition.query.order_by(Exhibition.created_at.desc()).limit(6).all()
    return render_template('index.html', exhibitions=exhibitions)


@main_bp.route('/profile/<username>')
def profile(username):
    user = User.query.filter_by(username=username).first_or_404()
    images = Image.query.filter_by(user_id=user.id).order_by(Image.uploaded_at.desc()).all()
    exhibitions = Exhibition.query.filter_by(user_id=user.id).order_by(Exhibition.created_at.desc()).all()
    return render_template('profile.html', profile_user=user, images=images, exhibitions=exhibitions,
                           get_image_url=get_image_url)


@main_bp.route('/upload', methods=['POST'])
@login_required
def upload():
    if 'file' not in request.files:
        flash('No file selected.', 'error')
        return redirect(url_for('main.profile', username=current_user.username))

    files = request.files.getlist('file')
    uploaded = 0
    current_used = get_total_storage_used()
    remaining = TOTAL_STORAGE_LIMIT - current_used

    for file in files:
        if file and file.filename and allowed_file(file.filename):
            file.seek(0, os.SEEK_END)
            file_size = file.tell()
            file.seek(0)

            if file_size > remaining:
                flash(f'Storage limit exceeded! Cannot upload "{file.filename}". '
                      f'Remaining space: {remaining / 1024 / 1024:.1f} MB. '
                      f'File size: {file_size / 1024 / 1024:.1f} MB.', 'error')
                continue

            filename, saved_size = save_upload(file)
            image = Image(
                filename=filename,
                original_name=secure_filename(file.filename),
                title=request.form.get('title', ''),
                description=request.form.get('description', ''),
                user_id=current_user.id,
                file_size=saved_size
            )
            db.session.add(image)
            uploaded += 1
            remaining -= saved_size

    db.session.commit()
    flash(f'{uploaded} image(s) uploaded successfully!', 'success')
    return redirect(url_for('main.profile', username=current_user.username))


@main_bp.route('/image/delete/<int:image_id>', methods=['POST'])
@login_required
def delete_image(image_id):
    image = Image.query.get_or_404(image_id)
    if image.user_id != current_user.id:
        flash('You do not have permission to delete this image.', 'error')
        return redirect(url_for('main.index'))

    delete_file(image.filename)

    db.session.delete(image)
    db.session.commit()
    flash('Image deleted.', 'success')
    return redirect(url_for('main.profile', username=current_user.username))


@main_bp.route('/avatar/upload', methods=['POST'])
@login_required
def upload_avatar():
    if 'avatar' not in request.files:
        flash('No file selected.', 'error')
        return redirect(url_for('main.profile', username=current_user.username))

    file = request.files['avatar']
    if file and file.filename and allowed_file(file.filename):
        # Delete old avatar if not default
        delete_file(current_user.avatar)

        filename, _ = save_upload(file)
        current_user.avatar = filename
        db.session.commit()
        flash('Avatar updated!', 'success')
    else:
        flash('Invalid file type.', 'error')

    return redirect(url_for('main.profile', username=current_user.username))


@main_bp.route('/profile/edit', methods=['GET', 'POST'])
@login_required
def edit_profile():
    if request.method == 'POST':
        bio = request.form.get('bio', '').strip()
        current_user.bio = bio
        db.session.commit()
        flash('Profile updated!', 'success')
        return redirect(url_for('main.profile', username=current_user.username))
    return render_template('edit_profile.html')


# Exhibition routes
@main_bp.route('/exhibition/create', methods=['GET', 'POST'])
@login_required
def create_exhibition():
    if request.method == 'POST':
        title = request.form.get('title', '').strip()
        description = request.form.get('description', '').strip()

        if not title:
            flash('Please enter an exhibition title.', 'error')
            return render_template('create_exhibition.html')

        exhibition = Exhibition(title=title, description=description, user_id=current_user.id)
        db.session.add(exhibition)
        db.session.commit()
        flash('Exhibition created!', 'success')
        return redirect(url_for('main.edit_exhibition', exhibition_id=exhibition.id))

    return render_template('create_exhibition.html')


@main_bp.route('/exhibition/<int:exhibition_id>')
def view_exhibition(exhibition_id):
    exhibition = Exhibition.query.get_or_404(exhibition_id)
    items = ExhibitionItem.query.filter_by(exhibition_id=exhibition_id).order_by(ExhibitionItem.order).all()
    return render_template('exhibition.html', exhibition=exhibition, items=items, get_image_url=get_image_url)


@main_bp.route('/exhibition/<int:exhibition_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_exhibition(exhibition_id):
    exhibition = Exhibition.query.get_or_404(exhibition_id)
    if exhibition.user_id != current_user.id:
        flash('Permission denied.', 'error')
        return redirect(url_for('main.index'))

    if request.method == 'POST':
        exhibition.title = request.form.get('title', '').strip()
        exhibition.description = request.form.get('description', '').strip()
        db.session.commit()
        flash('Exhibition updated!', 'success')
        return redirect(url_for('main.view_exhibition', exhibition_id=exhibition.id))

    user_images = Image.query.filter_by(user_id=current_user.id).order_by(Image.uploaded_at.desc()).all()
    items = ExhibitionItem.query.filter_by(exhibition_id=exhibition_id).order_by(ExhibitionItem.order).all()
    return render_template('edit_exhibition.html', exhibition=exhibition, user_images=user_images, items=items,
                           get_image_url=get_image_url)


@main_bp.route('/exhibition/<int:exhibition_id>/add_image', methods=['POST'])
@login_required
def add_exhibition_image(exhibition_id):
    exhibition = Exhibition.query.get_or_404(exhibition_id)
    if exhibition.user_id != current_user.id:
        return jsonify({'error': 'Permission denied'}), 403

    image_id = request.form.get('image_id', type=int)
    caption = request.form.get('caption', '')

    image = Image.query.get_or_404(image_id)
    if image.user_id != current_user.id:
        return jsonify({'error': 'Permission denied'}), 403

    max_order = db.session.query(db.func.max(ExhibitionItem.order)).filter_by(exhibition_id=exhibition_id).scalar()
    new_order = (max_order or 0) + 1

    item = ExhibitionItem(exhibition_id=exhibition_id, image_id=image_id, order=new_order, caption=caption)
    db.session.add(item)
    db.session.commit()

    return jsonify({'success': True, 'item_id': item.id})


@main_bp.route('/exhibition/<int:exhibition_id>/remove_image/<int:item_id>', methods=['POST'])
@login_required
def remove_exhibition_image(exhibition_id, item_id):
    exhibition = Exhibition.query.get_or_404(exhibition_id)
    if exhibition.user_id != current_user.id:
        return jsonify({'error': 'Permission denied'}), 403

    item = ExhibitionItem.query.get_or_404(item_id)
    db.session.delete(item)
    db.session.commit()

    return jsonify({'success': True})


@main_bp.route('/exhibition/<int:exhibition_id>/reorder', methods=['POST'])
@login_required
def reorder_exhibition(exhibition_id):
    exhibition = Exhibition.query.get_or_404(exhibition_id)
    if exhibition.user_id != current_user.id:
        return jsonify({'error': 'Permission denied'}), 403

    data = request.get_json()
    for idx, item_id in enumerate(data.get('order', [])):
        item = ExhibitionItem.query.get(item_id)
        if item and item.exhibition_id == exhibition_id:
            item.order = idx
    db.session.commit()

    return jsonify({'success': True})


@main_bp.route('/exhibition/<int:exhibition_id>/delete', methods=['POST'])
@login_required
def delete_exhibition(exhibition_id):
    exhibition = Exhibition.query.get_or_404(exhibition_id)
    if exhibition.user_id != current_user.id:
        flash('Permission denied.', 'error')
        return redirect(url_for('main.index'))

    db.session.delete(exhibition)
    db.session.commit()
    flash('Exhibition deleted.', 'success')
    return redirect(url_for('main.profile', username=current_user.username))


@main_bp.route('/gallery')
def gallery():
    page = request.args.get('page', 1, type=int)
    images = Image.query.order_by(Image.uploaded_at.desc()).paginate(page=page, per_page=20, error_out=False)
    return render_template('gallery.html', images=images, get_image_url=get_image_url)
