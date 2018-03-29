#! /usr/bin/env python
import sys
import argparse
import yaml
import docker

def read_image_list_file(filename):
    with open(filename) as file:
        try:
            image_list_file = yaml.load(file)
        except yaml.YAMLError as e:
            error("Error: failed to parse image list: %s" % e)
    return image_list_file

def has_tag(image):
    return len(image.split(':')) == 2

def error(s):
    print(s)
    sys.exit(1)

image_list = read_image_list_file("imagelist.yml")['images']
dc = docker.client.from_env()

for image in image_list:
    src = image['src']
    dest = image['dest']
    if not has_tag(src) or not has_tag(dest):
        error("Error: src or dest for image [%s] is not tagged!" % src )

    print("Pulling image [%s]" % src)
    try:
        src_image = dc.images.pull(src)
    except docker.errors.APIError as e:
        print(e)

    print("Tagging image [%s] as [%s]" % (src, dest))
    if not src_image.tag(dest):
        error("Error: Can't tag image [%s] as [%s]" % (src, dest))

    print("Pushing image [%s]" % dest)
    try:
        for l in dc.images.push(dest, stream=True):
            print l,
        print(80 * "#"  )
    except docker.errors.APIError as e:
        print(e)
