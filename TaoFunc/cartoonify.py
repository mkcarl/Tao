import cv2
import numpy as np

class Cartoonify:
    # Loading the image file
    @staticmethod
    def read_img(img_location):
        return cv2.imread(img_location)


    # Show the image in a window
    @staticmethod
    def show_img(img):
        cv2.imshow('Image preview', img)
        cv2.waitKey(0)
        cv2.destroyAllWindows()


    # Save image
    @staticmethod
    def save_img(img, filename):
        cv2.imwrite(filename, img)


    # Find the edge
    @staticmethod
    def edge_mask(img, line_size, blur_value):
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        gray_blur = cv2.medianBlur(gray, blur_value)
        edges = cv2.adaptiveThreshold(gray_blur, 255, cv2.ADAPTIVE_THRESH_MEAN_C, cv2.THRESH_BINARY, line_size, blur_value)
        return edges


    # Color quantization using K-means algorithm
    @staticmethod
    def color_quantization(img, k):
        data = np.float32(img).reshape((-1, 3))

        # Determine criteria
        criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 20, 0.001)

        # Implementing K-Means
        ret, label, center = cv2.kmeans(data, k, None, criteria, 10, cv2.KMEANS_RANDOM_CENTERS)
        center = np.uint8(center)
        result = center[label.flatten()]
        result = result.reshape(img.shape)
        return result


    # Reducing noise in image
    @staticmethod
    def blur_img(img, d, sigmaColor, sigmaSpace):
        blurred = cv2.bilateralFilter(
            img,
            d=d,
            sigmaColor=sigmaColor,
            sigmaSpace=sigmaSpace
        )
        return blurred


    # Combine the images
    @staticmethod
    def combine(edge, reduced_img):
        return cv2.bitwise_and(reduced_img, reduced_img, mask=edge)


    @staticmethod
    def wrapper(inputImg:str,
                 lineSize:int=9,
                 blurValue:int=9,
                 kCluster:int=9,
                 filterSize:int=5,
                 sigma:int=200):
        # print("Starting ML algorithm")
        img = Cartoonify.read_img(inputImg)
        img2 = Cartoonify.edge_mask(img, lineSize, blurValue)
        img3 = Cartoonify.color_quantization(img, kCluster)
        img4 = Cartoonify.blur_img(img3, filterSize, sigma, sigma)
        img5 = Cartoonify.combine(img2, img4)
        return img5


if __name__ == "__main__":
    ctn = Cartoonify()
    Cartoonify.wrapper("D:/PythonCode/Cartoonify/input/20200830_180248.jpg")
