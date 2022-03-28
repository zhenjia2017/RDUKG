import torch
import torch.utils.data as Data


class ReData(Data.Dataset):
    def change_dataset(self, folder, dataset):
        self.data = self.all_data[folder][dataset]

    def __init__(self, data):
        super(ReData, self).__init__()
        self.entity_tag2ids = data["entity_tag2ids"]
        self.entity_ids2tag = data["entity_ids2tag"]
        self.relation_tag2ids = data["relation_tag2ids"]
        self.relation_ids2tag = data["relation_ids2tag"]
        self.all_data = data["data"]

    def __getitem__(self, index):
        data = self.data[index]
        return {
            "length": data["length"],
            "word2vec": data["word2vec"],
            "subject": data["subject"],
            "object": data["object"],
            "sub_pos": data["sub_pos"],
            "obj_pos": data["obj_pos"],
            "relation": data["relation"],
            "mask1": data["mask1"],
            "mask2": data["mask2"],
        }

    def __len__(self):
        return len(self.data)
