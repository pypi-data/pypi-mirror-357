from flask import Blueprint, render_template, request

from simple_image_gallery.services.images import ImageService

slideshow_bp = Blueprint('slideshow', __name__)


@slideshow_bp.get('/slideshow')
def slideshow(service: ImageService):
    # Get query parameters
    sort = request.args.get('sort', 0, int)
    # Get image paths
    image_paths = service.get_image_paths(sort, min_items=service.gallery_slideshow_min_batch_size)
    # Render the template
    template_vars = {
        'sort': sort,
        'images': image_paths,
        'header': service.gallery_header,
        'brand_name': service.gallery_brand_name,
        'min_items': service.gallery_slideshow_min_batch_size
    }
    return render_template('slideshow.html', **template_vars)
