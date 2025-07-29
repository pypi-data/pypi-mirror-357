from torch.utils.data import Dataset
import pandas as pd
from PIL import Image

class DeepfakeDataset(Dataset):
    def __init__(self, pandas_dataframe: pd.DataFrame):
        try:
            assert isinstance(pandas_dataframe, pd.DataFrame)
            assert "image_paths" in pandas_dataframe.columns
            assert "labels" in pandas_dataframe.columns
            assert set(pandas_dataframe.labels.unique()).issubset({0, 1})
        except Exception as e:
            raise ValueError(f"dataset validation failed! {str(e)}")

        self.dataframe = pandas_dataframe

    def __len__(self):
        return len(self.dataframe)

    def __str__(self):
        return f"{len(self.dataframe)} images."

    def __getitem__(self, idx):
        row = self.dataframe.iloc[idx]
        image = self.load_image(row["image_paths"])
        return {"pixel_values": image, "labels": row["labels"]}

    def load_image(self, path: str):
        """
        Abstracted image loading function. Override this in a subclass for custom loading/processing.
        """
        return Image.open(path).convert("RGB")
