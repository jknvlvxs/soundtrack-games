import os

FOLDER = "/app/dataset/videos_tensors/train"

def main():
    folder_par_dir = os.path.abspath(os.path.join(FOLDER, os.pardir))

    for file in os.listdir(FOLDER):
        current_path = os.path.join(FOLDER, file)
        new_path = os.path.join(folder_par_dir, file)

        os.rename(current_path, new_path)

if __name__ == "__main__":
    main()