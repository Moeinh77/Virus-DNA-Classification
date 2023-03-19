import torch
import os
import pandas as pd


class HF_dataset(torch.utils.data.Dataset):
    """
    A class to create a dataset for the HuggingFace transformers

    Parameters
    ----------
    input_ids : torch.tensor
        The input ids of the sequences
    attention_masks : torch.tensor
        The attention masks of the sequences
    labels : torch.tensor
        The labels of the sequences

    Returns
    -------
    torch.utils.data.Dataset
        A dataset compatible with the HuggingFace transformers

    """

    def __init__(self, input_ids, attention_masks, labels):
        self.input_ids = input_ids
        self.attention_masks = attention_masks
        self.labels = labels

    def __len__(self):
        return len(self.labels)

    def __getitem__(self, index):
        return {
            "input_ids": torch.tensor(self.input_ids[index]),
            "attention_mask": torch.tensor(self.attention_masks[index]),
            "labels": torch.tensor(self.labels[index]),
        }


def val_datasets_generator(
    tokenizer,
    KMER,
    val_dir="data/TestData",
):
    """
    This function generates a validation dataset for the HuggingFace transformers
    by reading the CSV files from the validation directory a yielding them one by one

    Parameters
    ----------
    tokenizer : transformers.PreTrainedTokenizer
        The tokenizer to be used for the dataset
    KMER : int
        The length of the K-mers to be used
    val_dir : str, optional
        The directory containing the validation CSV files, by default "data/TestData"
    
    Yields
    -------
    torch.utils.data.Dataset
        A dataset compatible with the HuggingFace transformers
    
    """
    
    for file in os.listdir(val_dir):
        df_test = pd.read_csv(f"{val_dir}/{file}")
        print(file, len(df_test))
        val_kmers, labels_val = [], []

        cls = "CLASS" if "CLASS" in df_test.columns else "Class"

        for seq, label in zip(df_test["SEQ"], df_test[cls]):
            kmer_seq = return_kmer(seq, K=KMER)
            val_kmers.append(kmer_seq)
            labels_val.append(label - 1)
        val_encodings = tokenizer.batch_encode_plus(
            val_kmers,
            max_length=512,
            pad_to_max_length=True,
            truncation=True,
            return_attention_mask=True,
            return_tensors="pt",
        )
        val_dataset = HF_dataset(
            val_encodings["input_ids"], val_encodings["attention_mask"], labels_val
        )
        yield val_dataset


def return_kmer(seq, K=6):
    """
    This function outputs the K-mers of a sequence

    Parameters
    ----------
    seq : str
        A single sequence to be split into K-mers
    K : int, optional
        The length of the K-mers, by default 6

    Returns
    -------
    kmer_seq : str
        A string of K-mers separated by spaces
    """

    kmer_list = []
    for x in range(len(seq) - K + 1):
        kmer_list.append(seq[x : x + K])

    kmer_seq = " ".join(kmer_list)
    return kmer_seq
