from PIL import Image
from manuscript.detectors import EASTInfer

# инициализация
det = EASTInfer(score_thresh=0.95)

# инфер
page, image = det.infer(r"C:\Users\USER\Desktop\gravitatsiya_1421_resized.jpg", vis=True)
print(page)

pil_img = Image.fromarray(image)

pil_img.show()
