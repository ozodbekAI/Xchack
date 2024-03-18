import cv2
import numpy as np
from insightface.app import FaceAnalysis
import json
import faiss
from datetime import datetime


class Functions():
    def __init__(self) -> None:
        self.app = FaceAnalysis()
        self.app.prepare(ctx_id=2, det_size=(640, 640))
        
    
    def load_embeddings(self, file_path):
        try:
            with open(file_path, 'r') as json_file:
                return json.load(json_file)
        except IOError as e:
            print(f"Ошибка при чтении файла: {e}")
            return {}

    def create_faiss_index(self, embeddings):
        d = embeddings.shape[1]
        index = faiss.IndexFlatL2(d)
        index.add(embeddings) # type: ignore
        return index
    

    def get_index(self):
        stored_embeddings = self.load_embeddings('faces.json')
        embeddings = np.array([value for value in stored_embeddings.values()]).astype('float32')


        return self.create_faiss_index(embeddings)
    
    def get_found_labels(self, frame):

        names = list(self.load_embeddings("faces.json").keys())
        
        index = self.get_index()

        faces = self.app.get(frame)

        found_users = []

        for face in faces:
            current_embedding = np.array(face.embedding, dtype="float32").reshape(1, -1)
            distances, indices = index.search(current_embedding, 1)

            if distances[0][0] < 600:
                found_users.append(
                    {
                        "name": names[indices[0][0]],
                        "found_time": datetime.utcnow().strftime('%Y-%m-%d %H:%M'),
                    }
                )
            else:
                found_users.append(
                    {
                        "name": "Begona",
                        "found_time": datetime.utcnow().strftime('%Y-%m-%d %H:%M'),
                    }
                )
        
        return found_users
    
    def get_image_embedding(self, img_path):
        try:
            frame = cv2.imread(img_path)
            if frame is None:
                print(f"Error: Unable to read the image at '{img_path}'.")
                return

            faces = self.app.get(frame)

            if len(faces) == 1:
                current_embedding = np.array(faces[0].embedding, dtype="float32").reshape(1, -1)

                return current_embedding.tolist()[0]
            
            elif len(faces) == 0:
                print("No faces detected in the image.")
            elif len(faces) > 1:
                print("More than one face detected. Please provide an image with a single face.")
            else:
                print("Error: An issue occurred while processing the image.")
        except Exception as e:
            print(f"Error: {e}")

   
