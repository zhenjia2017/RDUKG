import torch
import torch.utils.data as Data


class NerData(Data.Dataset):
    def change_dataset(self, folder, dataset):
        self.data = self.all_data[folder][dataset]

    def __init__(self, data):
        super(NerData, self).__init__()
        self.tag2ids = data["tag2ids"]
        self.ids2tag = data["ids2tag"]
        self.all_data = data["data"]

    def __getitem__(self, index):
        data = self.data[index]
        return {
            "length": data["length"],
            "word2vec": data["word2vec"],
            "lexicon": data["lexicon"],
            "label": data["label"],
            "mask": data["mask"],
        }

    def __len__(self):
        return len(self.data)
