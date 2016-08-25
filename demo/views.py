from django.shortcuts import render
from django.http import JsonResponse
from django.conf import settings
from channels import Group

from demo.sender import vqa
from demo.utils import log_to_terminal

import demo.constants as constants
import uuid
import os
import random
import traceback
import urllib2


def vqa(request, template_name="vqa/vqa.html"):
    socketid = uuid.uuid4()
    if request.method == "POST":
        # get the parameters from client side
        try:
            socketid = request.POST.get('socketid')
            input_question = request.POST.get('question', '')
            img_path = request.POST.get('img_path')
            img_path = urllib2.unquote(img_path)

            abs_image_path = os.path.join(settings.BASE_DIR, str(img_path[1:]))
            out_dir = os.path.dirname(abs_image_path)

            # Run the VQA wrapper
            log_to_terminal(socketid, {"terminal": "Starting Visual Question Answering job..."})
            response = grad_cam_vqa(str(abs_image_path), str(input_question), socketid)
        except Exception, err:
            log_to_terminal(socketid, {"terminal": traceback.print_exc()})

    demo_images = get_demo_images(constants.COCO_IMAGES_PATH)
    return render(request, template_name, {"demo_images": demo_images, 'socketid': socketid})


def file_upload(request):
    if request.method == "POST":
        image = request.FILES['file']
        demo_type = request.POST.get("type")

        if demo_type == "vqa":
            dir_type = constants.VQA_CONFIG['image_dir']
        elif demo_type == "classification":
            dir_type = constants.CLASSIFICATION_CONFIG['image_dir']
        elif demo_type == "captioning":
            dir_type = constants.CAPTIONING_CONFIG['image_dir']

        random_uuid = uuid.uuid1()
        # handle image upload
        output_dir = os.path.join(dir_type, str(random_uuid))

        if not os.path.exists(output_dir):
            os.makedirs(output_dir)

        img_path = os.path.join(output_dir, str(image))
        handle_uploaded_file(image, img_path)
        return JsonResponse({"file_path": img_path.replace(settings.BASE_DIR, '')})    


def handle_uploaded_file(f, path):
    with open(path, 'wb+') as destination:
        for chunk in f.chunks():
            destination.write(chunk)


def get_demo_images(demo_images_path):
    try:
        demo_images = [random.choice(next(os.walk(demo_images_path))[2]) for i in range(6)]
        demo_images = [os.path.join(constants.COCO_IMAGES_PATH, x) for x in demo_images]
    except:
        images = ['img1.jpg', 'img2.jpg', 'img3.jpg', 'img4.jpg', 'img5.jpg', 'img6.jpg',]
        demo_images = [os.path.join(settings.STATIC_URL, 'images', x) for x in images]

    return demo_images
