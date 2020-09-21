import numpy as np
import cv2
import imutils
    
# based on the following blog post: https://www.pyimagesearch.com/2015/01/26/multi-scale-template-matching-using-python-opencv/
class MultiScaleTemplateMatcher:
    def __init__(self, template):
        self.template = template
        self.w, self.h = template.shape[::-1]
    
    def match_image(self, img: np.array, threshold=3000000):
        found = None

        # loop over the scales of the image
        for scale in np.linspace(0.2, 1.0, 20)[::-1]:
            # resize the image according to the scale, and keep track
            # of the ratio of the resizing
            resized = imutils.resize(img, width = int(img.shape[1] * scale))
            r = img.shape[1] / float(resized.shape[1])

            # if the resized image is smaller than the template, then break
            # from the loop
            if resized.shape[0] < self.h or resized.shape[1] < self.w:
                break

            # detect edges in the resized, grayscale image and apply template
            # matching to find the template in the image
            edged = cv2.Canny(resized, 50, 200)
            result = cv2.matchTemplate(edged, self.template, cv2.TM_CCOEFF)

            (_, max_val, _, max_loc) = cv2.minMaxLoc(result)

            # if we have found a new maximum correlation value, then update
            # the bookkeeping variable
            if found is None or max_val > found[0]:
                found = (max_val, max_loc, r)

        if not found:
            return None

        # unpack the bookkeeping variable and compute the (x, y) coordinates
        # of the bounding box based on the resized ratio

        (max_val, max_loc, r) = found

        #print(max_val)

        if max_val < threshold:
            return None

        (startX, startY) = (int(max_loc[0] * r), int(max_loc[1] * r))
        (endX, endY) = (int((max_loc[0] + self.w) * r), int((max_loc[1] + self.h) * r))

        return ((startX, startY), (endX, endY))