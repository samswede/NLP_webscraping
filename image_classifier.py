from torchvision import models, transforms
from PIL import Image

class ImageClassifier:
    def __init__(self):
        # Load the pre-trained model
        self.model = models.resnet50(pretrained=True)
        
        # The transform function to apply to the images before feeding them into the model
        self.transform = transforms.Compose([transforms.Resize(256),
                                             transforms.CenterCrop(224),
                                             transforms.ToTensor(),
                                             transforms.Normalize(mean=[0.485, 0.456, 0.406],
                                                                  std=[0.229, 0.224, 0.225])])
    def classify(self, image_path):
        # Open the image file
        img = Image.open(image_path)
        
        # Apply the transformations
        img_t = self.transform(img)
        
        # Add an extra batch dimension since pytorch treats all images as batches
        img_t = img_t.unsqueeze_(0)
        
        # Pass the image through the model and get the raw output
        output = self.model(img_t)
        
        # Apply a threshold to the output to get the labels
        labels = (output > 0.5).squeeze().tolist()

        return labels
