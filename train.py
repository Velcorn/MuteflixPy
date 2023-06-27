import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import Dataset, DataLoader, random_split
from torchvision import transforms, models
from PIL import Image
import os


# Define the custom dataset
class AdDataset(Dataset):
    def __init__(self, root_dir, transform=None):
        self.root_dir = root_dir
        self.transform = transform
        self.images = []
        self.labels = []

        ad_images_path = os.path.join(self.root_dir, 'ad')
        no_ad_images_path = os.path.join(self.root_dir, 'no_ad')

        self.images.extend([os.path.join(ad_images_path, img) for img in os.listdir(ad_images_path)])
        self.labels.extend([1] * len(os.listdir(ad_images_path)))

        self.images.extend([os.path.join(no_ad_images_path, img) for img in os.listdir(no_ad_images_path)])
        self.labels.extend([0] * len(os.listdir(no_ad_images_path)))

    def __len__(self):
        return len(self.images)

    def __getitem__(self, idx):
        img_name = self.images[idx]
        image = Image.open(img_name).convert('RGB')

        if self.transform:
            image = self.transform(image)

        label = self.labels[idx]

        return image, label


# Define the image transformations
transform = transforms.Compose([
    transforms.Resize((224, 224)),
    transforms.ToTensor(),
    transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])
])

# Set the path to the dataset folder
dataset_path = 'images'

# Create the dataset
dataset = AdDataset(dataset_path, transform=transform)

# Split the dataset into train and validation sets
train_ratio = 0.9
train_size = int(train_ratio * len(dataset))
val_size = len(dataset) - train_size
train_set, val_set = random_split(dataset, [train_size, val_size])

# Create the data loaders for train and validation sets
batch_size = 16
train_loader = DataLoader(train_set, batch_size=batch_size, shuffle=True)
val_loader = DataLoader(val_set, batch_size=batch_size, shuffle=True)

# Define the model architecture
model = models.resnet50()
num_features = model.fc.in_features
model.fc = nn.Linear(num_features, 2)  # Binary classification, 2 output classes

# Set device (CPU or GPU)
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
model = model.to(device)

# Define the loss function and optimizer
criterion = nn.CrossEntropyLoss()
optimizer = optim.SGD(model.parameters(), lr=0.001, momentum=0.9)

# Train the model
num_epochs = 10

for epoch in range(num_epochs):
    model.train()

    for images, labels in train_loader:
        images = images.to(device)
        labels = labels.to(device)

        optimizer.zero_grad()

        outputs = model(images)
        loss = criterion(outputs, labels)
        loss.backward()
        optimizer.step()

    print(f"Epoch [{epoch + 1}/{num_epochs}] Training Loss: {loss.item()}")

    # Validation
    model.eval()
    val_loss = 0
    correct = 0
    total = 0

    with torch.no_grad():
        for images, labels in val_loader:
            images = images.to(device)
            labels = labels.to(device)

            outputs = model(images)
            val_loss += criterion(outputs, labels).item()

            _, predicted = outputs.max(1)
            total += labels.size(0)
            correct += predicted.eq(labels).sum().item()

    val_loss /= len(val_loader)
    accuracy = 100.0 * correct / total

    print(f"Epoch [{epoch + 1}/{num_epochs}] Validation Loss: {val_loss:.4f} Accuracy: {accuracy:.2f}%")

# Save the model
torch.save(model.state_dict(), 'model/model.pth')

print("Training finished!")
