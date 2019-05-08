from skimage import io, img_as_ubyte, img_as_float
from skimage.transform import resize
import glob
import os
from zipfile import ZipFile 

def read_and_resize_img(filepath):
    img = img_as_ubyte(io.imread(filepath))
    resized_img = resize(img, (448, 416), anti_aliasing=True)
    return resized_img

def get_all_img_paths(scraper_dir):
    all_img_paths = []
    websites = ["unsplash", "amazon"]
    for w in websites:
        img_dir = os.path.join(scraper_dir, w, "imgs")
        # Get image  paths
        all_img_paths.extend(glob.glob(os.path.join(img_dir, '*', '*'))) # ex. imgs/category/img1.png
    return all_img_paths

def main(): 
    scraper_dir = "./scraper"
    common_imgs_dir = "./imgs"
    #  Make the common directory if it hasn't already been made
    if not os.path.exists(common_imgs_dir):
        os.makedirs(common_imgs_dir)
    # Grab all filepaths
    img_paths = get_all_img_paths(scraper_dir)
    # Read in, resize, and write imgs out to their same image path, minus the website (so they're put all into one imgs directory)
    for path in img_paths: 
        resized_img = read_and_resize_img(path)
        split = path.split("/")
        category = split[4]
        img_name = split[5]
        common_category_dir = os.path.join(common_imgs_dir, category)
        common_path =  os.path.join(common_category_dir, img_name)
        if not os.path.exists(common_category_dir):
            os.makedirs(common_category_dir)
        io.imsave(common_path, img_as_ubyte(resized_img))

    print('All files resized and put into ./imgs')         
  
  
if __name__ == "__main__": 
    main() 