import argparse
import os
from deploy.load_model import predict_image, get_letter

def main():
    parser = argparse.ArgumentParser(description="Predict image using trained model.")
    parser.add_argument("image_path", help="Path to the image file")
    args = parser.parse_args()

    image_path = args.image_path

    if not os.path.exists(image_path):
        print(f"Error: File '{image_path}' not found.")
        return

    print(f"Predicting image: {image_path}")
    results = predict_image(image_path)
    letter = get_letter(results)

    print("\nPrediction Results:")
    print("-------------------")
    print(f"Raw Output: {results}")
    print(f"Predicted Letter: {letter}")

if __name__ == "__main__":
    main()
